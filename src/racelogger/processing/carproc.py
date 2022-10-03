import logging
import math
import re
import sys
from enum import Enum

from racelogger.processing.singlecarproc import CarData
from racelogger.processing.singlecarproc import CarsManifest
from racelogger.processing.singlecarproc import CarState
from racelogger.processing.singlecarproc import PitBoundaries
from racelogger.processing.speedmap import SpeedMap
from racelogger.util.utils import gate
from racelogger.util.utils import get_track_length_in_meters


def delta_distance(a,b):
    if a >= b:
        return a-b
    else:
        return a+1-b

def delta_to_prev(a,b):
    d = abs(a-b)
    if d > 0.5:
        return 1-d
    else:
        return d

def laptimeStr(t):
    work = t;
    minutes = t // 60;
    work -= minutes * 60;
    seconds = math.trunc(work);
    work -= seconds;
    hundrets = math.trunc(work * 100);
    if minutes > 0 :
        return f"{minutes:.0f}:{seconds:02d}.{hundrets:02d}"
    else:
        return f"{seconds:02d}.{hundrets:02d}"

def coalesce(arg):
    if type(arg) == int:
        return arg
    if type(arg) == float:
        return arg
    return 0






class CarProcessor():
    """
    the main processor for handling data around the complete car field.
    This means standings and the like are processed here as well as relative gaps and distances.
    Data for single cars is processed in CarData.
    """
    def __init__(self,driver_proc=None, current_ir=None, manifest=CarsManifest) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.driver_proc = driver_proc
        self.lookup = {}
        self.prev_dist_pct = []
        self.prev_time = current_ir['SessionTime']
        self.sectors = current_ir['SplitTimeInfo']['Sectors'];
        self.manifest = manifest + [f's{x+1}' for x in range(len(self.sectors))]

        if current_ir['WeekendInfo']['TeamRacing'] == 0:
            self.manifest.remove('teamName')
        if current_ir['WeekendInfo']['NumCarClasses'] == 1:
            self.manifest.remove('carClass')
        

        self.overall_best_sectors = [sys.maxsize for x in range(len(self.sectors))]
        self.overall_best_lap = sys.maxsize
        self.class_best_laps = [] # todo!

        self.about_to_finish_marker = [] # will be set when checkered flag is issues
        self.winner_crossed_the_line = False # you guess when it will be true

        self.track_length = get_track_length_in_meters(current_ir['WeekendInfo']['TrackLength'])
        print(f"TrackLength: {self.track_length}")
        self.min_move_dist_pct = 0.1/self.track_length # if a car doesn't move 10cm in 1/60s
        self.last_standings = current_ir['SessionInfo']['Sessions'][current_ir['SessionNum']]['ResultsPositions']
        self.speedmap = SpeedMap(self.track_length)
        self.pit_boundaries = PitBoundaries()

    def collect_caridx_to_process(self, ir):
        ret = [item['CarIdx'] for item in filter(lambda d: d['IsSpectator']==0 and d['CarIsPaceCar']==0,ir['DriverInfo']['Drivers'])]
        return ret

    def process(self,ir,msg_proc):
        for idx in self.collect_caridx_to_process(ir):
            if idx not in self.lookup.keys():
                work = CarData(carIdx=idx,manifest=self.manifest, num_sectors=len(self.sectors), driver_proc=self.driver_proc,pit_boundaries=self.pit_boundaries)
                work.last = -1
                work.best = -1
                self.lookup[idx] = work
            else:
                work = self.lookup.get(idx)

            work.process(ir)

            if work.processState in [CarState.RUN, CarState.SLOW, CarState.PIT]:
                work = self.compute_times(work,ir, msg_proc)

                speed = self.calc_speed(ir, idx)
                work.speed = speed
                work.post_process(msg_proc=msg_proc)

        # every car is processed, now for common stuff in this step
        self.calc_delta(ir)
        cur_standings = ir['SessionInfo']['Sessions'][ir['SessionNum']]['ResultsPositions']
        if cur_standings != self.last_standings:
            self.process_standings(cur_standings,msg_proc)

        self.prev_dist_pct = ir['CarIdxLapDistPct'][:] # create a copy for next run
        self.prev_time = ir['SessionTime']


    def process_standings(self, st, msg_proc):
        # Note: we get the standings a little bit after a car crossed the line (about a second)
        #
        if (st == None):
            self.logger.debug(f"st is none????")
            return
        self.logger.debug(f"new standings arrived")
        ob_idx = None
        for line in st:
            work = self.lookup.get(line['CarIdx'])
            if work == None:
                # may happen, if we reconnected during a race. At final standings there may be more entries than we thought there are ;)
                work = CarData(self.manifest, len(self.sectors))
                work.last = -1
                work.best = -1
                self.lookup[line['CarIdx']] = work

            # Not sure if we need it here, too
            # if work['state'] == 'FIN':
            #     continue

            work.pos = line['Position']
            work.pic = line['ClassPosition']
            work.gap = line['Time']
            work.best = line['FastestTime']
            work.lastRaw = line['LastTime']
            duration = line['LastTime']
            if duration == None:
                # first lap, car may not crossed the line yet
                self.logger.warning(f"duration is None for carNum {work['num']}")
                continue
            if duration == -1:
                duration = work.lap_timings.lap.duration
                work.last = duration
            else:
                if duration < self.overall_best_lap:
                    ob_idx = line['CarIdx']
                    work.current_best = duration
                    work.last = [duration, "ob"]
                    work.marker_info = (line['LapsComplete'], "ob")
                    # if there are any other ob-laps, degrade them to pb
                    for check_other in self.lookup.values():
                        if type(check_other.last) is list and check_other.marker_info[1] == "ob" and check_other.carIdx != ob_idx:
                            self.logger.info(f"resetting ob to pb for {check_other.carIdx}-{check_other.carNum}")
                            check_other.marker_info = (line['LapsComplete'], "pb")
                            check_other.last[1] = "pb"


                    self.overall_best_lap = duration
                elif duration < work.current_best:
                    work.last = [duration, "pb"]
                    work.current_best = duration
                    work.marker_info = (line['LapsComplete'], "pb")
                    msg_proc.add_timing_info(line['CarIdx'], f'personal new best lap {laptimeStr(duration)}')
                else:
                    if work.marker_info[0] == line['LapsComplete'] and work.marker_info[1] != "":
                        work.last = [duration, work.marker_info[1]]
                    else:
                        work.last = duration
                        work.marker_info = (-1,"")

        if ob_idx != None:
            work = self.lookup.get(ob_idx)
            duration = getattr(work, 'last')
            if type(duration) is list:
                # msg_proc.add_timing_info(ob_idx, f'strange: {duration}')
                duration = duration[0]
            work.last = [duration , "ob"]
            msg_proc.add_timing_info(ob_idx, f'new overall best lap {laptimeStr(duration)}')

        self.last_standings = st


    def compute_times(self, carData, ir, msg_proc):
        trackPos = getattr(carData, 'trackPos')
        car_idx = getattr(carData, 'carIdx')
        i = len(self.sectors)-1
        while trackPos < self.sectors[i]['SectorStartPct']:
            i = i - 1
        # i holds the current sector
        if carData.current_sector == -1:
            carData.current_sector = i
            # don't compute this sector. on -1 we are pretty much rushing into a running race or just put into the car
            return carData

        if i == carData.current_sector:
            return carData

        # use this for debugging
        car_num = self.driver_proc.car_number(getattr(carData, 'carIdx'))

        # the prev sector is done (we assume the car is running in the correct direction)
        # but some strange things may happen: car spins, comes to a halt, drives in reverse direction and crosses the sector mark multiple times ;)
        # very rare, I hope
        # so we check if the current sector is the next "expected" sector
        expected_sector = (carData.current_sector + 1) % len(self.sectors)
        if i != expected_sector:
            # current sector does not match the expected next sector
            # self.logger.warn(f"car {car_num} not in expected sector. got value: {i} expect: {expected_sector}")
            return carData

        t = ir['SessionTime']
        # close the (now) previous sector
        sector = carData.lap_timings.sectors[carData.current_sector]

        # if the sector has no start time we ignore it. prepare the next one and leave
        if sector.start_time == -1:
            carData.current_sector = i
            sector = carData.lap_timings.sectors[i]
            sector.mark_start(t)
            return carData

        duration = sector.mark_stop(t)
        # handle the colors for best sector
        if duration < self.overall_best_sectors[carData.current_sector]:
            setattr(carData, f's{carData.current_sector+1}', [duration, "ob"]) # +1 because auf s1,s2,s3...
            self.overall_best_sectors[carData.current_sector] = duration
            # TODO: if another car has also an "ob" sector, downgrade it to "pb" or "cb" ;)
            manifest_sector = f's{carData.current_sector+1}'
            for other in self.lookup.values():
                if (other != carData):
                    sector_data = getattr(other, manifest_sector)
                    if type(sector_data) is list and sector_data[1] == 'ob':
                        sector_data[1] = 'pb'

            sector.best = duration
        elif duration < sector.best:
            setattr(carData, f's{carData.current_sector+1}', [duration, "pb"])
            sector.best = duration
        else:
            setattr(carData, f's{carData.current_sector+1}', sector.duration)

        # mark all sectors after this as old if first sector is done
        if carData.current_sector == 0:
            for x in range(i, len(self.sectors)):
                setattr(carData, f's{x+1}', [carData.lap_timings.sectors[x].duration, "old"])

        carData.current_sector = i
        # start the new current sector
        sector = carData.lap_timings.sectors[i]
        sector.mark_start(t)

        # compute own laptime
        if (i == 0):
            self.logger.info(f"car {car_num} crossed the line")

            ## TODO: StintLaps berechnen
            # mal schauen, ob das so geht. Evtl. noch Sonderbehandlung für Racefinish
            #carData.stintLap += 1

            if carData.lap_timings.lap.start_time == -1:
                self.logger.info(f"car {car_num} had start_time of -1. not recording this one")
            else:
                duration = carData.lap_timings.lap.mark_stop(t)
            if self.winner_crossed_the_line:
                carData.state = "FIN"
                carData.processState = CarState.FINISHED
                # we don't want the cool down lap to be counted
                carData.lap = getattr(carData, "lc")
                carData.stintLap -= 1 # remove +1 from above
                self.logger.info(f"car {car_num} finished the race")
                return carData
            else:
                if len(self.about_to_finish_marker) > 0:
                    lc = getattr(carData, "lc")
                    lap = getattr(carData, "lap")
                    ref = self.about_to_finish_marker[0][1]
                    self.logger.info(f"car {car_num} lap: {lap} ref: {ref} bool: {lap > ref}")
                    if lap > ref:
                        self.winner_crossed_the_line = True
                        carData.state = "FIN"
                        carData.processState = CarState.FINISHED
                        # we don't want the cool down lap to be counted
                        carData.lap = lc
                        carData.stintLap -= 1 # remove +1 from above
                        # setattr(carData, "state", "FIN")
                        self.logger.info(f"car {car_num} won the race")
                        return carData
                # return if winner crossed the line
            carData.lap_timings.lap.mark_start(t)

        return carData

    def race_starts(self, ir):
        t = ir['SessionTime']
        for work in self.lookup.values():
            work.lap_timings.lap.mark_start(t)

    def checkered_flag(self, ir):
        t = ir['SessionTime']
        # TODO: from now on we only want data for cars who still not have finished the race
        # we compute a marker by lc + trackPos. The next car that crosses the line with dist > marker is the winner
        # (Note: does not work if all cars currently on the leading lap do not reach the s/f)
        current_order = self.get_current_raceorder()
        self.about_to_finish_marker = current_order
        self.logger.info(f"about to finish marker: {self.about_to_finish_marker}")


    def get_current_raceorder(self):
        def standard_race_order():
            """
            this is used during the race
            """
            ret = [(i.carIdx, coalesce(i.lap)+coalesce(i.trackPos))  for i in self.lookup.values()]
            ret.sort(key = lambda k: k[1], reverse=True)
            return ret


        def race_ending_race_order():
            """
            this is used, when the first car has finished the race. We want some special treatment here.
            """
            ret = [(i.carIdx, i.pos)  for i in self.lookup.values() if coalesce(i.pos) > 0]
            ret.sort(key = lambda k: k[1], reverse=False)
            ret.extend((i.carIdx, i.pos)  for i in self.lookup.values() if i.pos < 1)
            return ret

        if (self.winner_crossed_the_line):
            current_race_order = race_ending_race_order()
        else:
            current_race_order = standard_race_order()

        return current_race_order

    def calc_speed(self, ir, idx):
        current_dist = ir['CarIdxLapDistPct'][idx]
        t = ir['SessionTime']
        if len(self.prev_dist_pct) != len(ir['CarIdxLapDistPct']):
            return -1
        move_dist_pct = delta_to_prev(gate(current_dist), gate(self.prev_dist_pct[idx]))
        delta_time = ir['SessionTime'] - self.prev_time
        if (delta_time != 0):
            if move_dist_pct < self.min_move_dist_pct or move_dist_pct > (1-self.min_move_dist_pct):
                if ir['CarIdxOnPitRoad'][idx] == False:
                    #self.logger.debug(f'STime: {ir["SessionTime"]:.0f} carIdx: {idx} curPctRaw: {current_dist} prevPctRaw: {self.prev_dist_pct[idx]} dist: {move_dist_pct} did not move min distance')
                    pass
                return 0

            speed = move_dist_pct*self.track_length/delta_time * 3.6

            if (speed > 400):
                self.logger.warning(f'STime: {ir["SessionTime"]:.0f} Speed > 400: {speed} carIdx: {idx} curPctRaw: {current_dist} prevPctRaw: {self.prev_dist_pct[idx]} dist: {move_dist_pct} dist(m): {move_dist_pct*self.track_length} deltaTime: {delta_time}')
                return -1
            else:
                if ir['CarIdxOnPitRoad'][idx] == False and speed > 0:
                    car_class_id = self.driver_proc.car_class_id(idx)
                    self.speedmap.process(current_dist, speed, car_class_id)
            return speed
        else:
            return 0

    def calc_delta(self, ir):
        current_race_order = self.get_current_raceorder()
        session_num = ir['SessionNum']
        if ir['SessionInfo']['Sessions'][session_num]['SessionType'] != 'Race':
            return

        current_pct = ir['CarIdxLapDistPct']
        for i in range(1, len(current_race_order)):
            item = current_race_order[i]
            if (item[1] < 0):
                continue
            work = self.lookup[item[0]]
            if work.state == 'OUT':
                continue
            if work.state == 'FIN':
                car_in_front = current_race_order[i-1][0]
                gap_of_car_in_front = getattr(self.lookup[car_in_front], 'gap')
                work.interval = getattr(work, 'gap') - gap_of_car_in_front
                continue # do not calc any other data for finished cars

            car_in_front_pos = current_pct[current_race_order[i-1][0]]
            current_car_pos = current_pct[item[0]]

            # data.car_idx_dist_meters[item[0]] =  delta_distance(gate(current_pct[current_race_order[i-1][0]]), gate(current_pct[item[0]])) * self.track_length
            work.dist =  delta_distance(gate(current_pct[current_race_order[i-1][0]]), gate(current_pct[item[0]])) * self.track_length
            if coalesce(getattr(work,'speed')) <= 0:
                work.interval = 999
            else:
                # x1 = filter(lambda x: x['CarIdx']==i, state.lastDI['Drivers'])
                # y = next(x1)
                for d in ir['DriverInfo']['Drivers']:
                    if d['CarIdx'] == i:
                        car_class_id = d['CarClassID']
                        if self.speedmap != None:
                            delta_by_car_class_speedmap = self.speedmap.compute_delta_time(car_class_id, car_in_front_pos, current_car_pos)
                            work.interval = delta_by_car_class_speedmap
                        else:
                            work.interval = 999

    def manifest_output(self):
        current_race_order = self.get_current_raceorder()
        ordered = [self.lookup[item[0]] for item in current_race_order]
        # self.logger.debug(ordered)
        return [[getattr(m, x) for x in self.manifest] for m in ordered]

    def speedmap_output(self):
        return self.speedmap.output_data()


