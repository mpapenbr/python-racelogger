import logging
import sys
from enum import Enum

from racelogger.util.utils import gate

CAR_SLOW_SPEED = 25
""" a car is considered to be slow if its speed is below this value"""

CarsManifest = ['state','carIdx','carNum','userName','teamName','car','carClass','pos','pic','lap','lc','gap','interval','trackPos','speed','dist','pitstops', 'stintLap','last','best']
"""
this is the base manifest for car data. Sector times may be added at the end.
On the other hand, items like "teamName, carClass" (and maybe others)
may be removed if they are not used in the recording session.
"""

class SectionTiming:
    """
    this class is used to measure a sector time or a complete lap time.
    The key attr identifies a sector or lap number
    """
    def __init__(self) -> None:
        self.start_time = -1
        self.stop_time = -1
        self.duration = -1
        self.best = sys.maxsize


    def mark_start(self,sessionTime):
        self.start_time = sessionTime

    def mark_stop(self,sessionTime):
        self.stop_time = sessionTime
        self.duration = self.stop_time - self.start_time
        return self.duration
        # self.best = min(self.best,self.duration)



class CarLaptiming:
    def __init__(self, num_sectors=0) -> None:
        self.lap = SectionTiming()
        self.sectors = [SectionTiming() for x in range(num_sectors)]

    def reset(self):
        pass

class CarState(Enum):
    INIT = 0
    RUN = 1
    PIT = 2
    FINISHED = 3
    OUT = 4
    SLOW = 5

class PitBoundaryData:
    """
    @param keep_hist use at most this many entries for computation

    @param min_hist build up at least this many entries before deciding about which entries to keep.
    """
    def __init__(self, keep_hist=21, min_hist=3) -> None:

        self.min = 0
        self.max = 0
        self.middle = 0
        self.hist = []
        self.keep_hist = keep_hist
        self.min_hist = min_hist

    def process(self, trackPos):
        """
        process the given trackPos. while
        """
        if len(self.hist) < self.keep_hist:
            self.hist.append(trackPos)
            self.compute_values()
            return
        self.hist.append(trackPos)

        if len(self.hist) % 2 == 1:
            self.hist.sort()
            self.hist = self.hist[1:-1]

    def compute_values(self):
        self.min = self.hist[0]
        self.max = self.hist[-1]
        self.middle = self.hist[len(self.hist)>>1]

    def __repr__(self) -> str:
        tmp = ", ".join([f"{e}" for e in self.hist] )
        return f'PitBoundaryData min: {self.min} max: {self.max} avg: {self.middle} hist: {tmp}'

class PitBoundaries():
    def __init__(self) -> None:
        self.pit_entry_boundary = PitBoundaryData()
        self.pit_exit_boundary = PitBoundaryData()

    def process_entry(self, trackPos):
        self.pit_entry_boundary.process(trackPos)
    def process_exit(self, trackPos):
        self.pit_exit_boundary.process(trackPos)
    def __repr__(self) -> str:
        return f'PitEntry: {self.pit_entry_boundary}\nPitExit: {self.pit_exit_boundary}\n'

class CarData:
    """
    this class holds data about a car during a race.
    No data history is stored here.
    """
    def __init__(self,carIdx=None, manifest=CarsManifest,num_sectors=0, driver_proc=None, pit_boundaries=None) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        for item in manifest:
            self.__setattr__(item, "")
        self.current_best = sys.maxsize
        self.carIdx = carIdx
        self.manifest = manifest
        self.slow_marker = False
        self.current_sector = -1
        self.stintLap = 0
        self.pitstops  = 0
        self.driver_proc = driver_proc
        self.lap_timings = CarLaptiming(num_sectors=num_sectors)
        self.pit_boundaries = pit_boundaries
        self.marker_info = (-1,"") # lapNo/marker


        self.processState = CarState.INIT
        self.stateSwitch = {
            CarState.INIT: self.state_init,
            CarState.RUN: self.state_racing,
            CarState.SLOW: self.state_racing_slow,
            CarState.PIT: self.state_pitting,
            CarState.FINISHED: self.state_finished,
            CarState.OUT: self.state_out_of_race,
        }
        self.postProcessStateSwitch = {
            CarState.INIT: self.state_post_process_noop,
            CarState.RUN: self.state_post_process_run,
            CarState.SLOW: self.state_post_process_slow,
            CarState.PIT: self.state_post_process_noop,
            CarState.FINISHED: self.state_post_process_noop,
            CarState.OUT: self.state_post_process_noop,
        }

    def state_init(self, ir):
        self.copy_standards(ir)
        self.trackPos = gate(ir['CarIdxLapDistPct'][self.carIdx])
        self.pos = ir['CarIdxPosition'][self.carIdx]
        self.pic = ir['CarIdxClassPosition'][self.carIdx]
        self.lap = ir['CarIdxLap'][self.carIdx]
        self.lc = ir['CarIdxLapCompleted'][self.carIdx]
        if ir['CarIdxLapDistPct'][self.carIdx] == -1:
            self.state= "OUT"
            self.processState = CarState.OUT
            return

        if ir['CarIdxOnPitRoad'][self.carIdx]:
            self.copy_when_racing(ir)
            self.state = "PIT"
            self.processState = CarState.PIT
            self.stintLap = 0
        else:
            self.copy_when_racing(ir)
            self.state = "RUN"
            self.processState = CarState.RUN

    def state_racing(self, ir):
        self.copy_standards(ir)
        if ir['CarIdxLapDistPct'][self.carIdx] == -1:
            self.state= "OUT"
            self.processState = CarState.OUT
            return

        if ir['CarIdxOnPitRoad'][self.carIdx] == False and ir['CarIdxLapCompleted'][self.carIdx]>self.lc:
            self.stintLap += 1

        self.copy_when_racing(ir)
        if ir['CarIdxOnPitRoad'][self.carIdx]:
            self.state = "PIT"
            self.pitstops += 1
            self.processState = CarState.PIT
            self.pit_boundaries.process_entry(ir['CarIdxLapDistPct'][self.carIdx])

    def state_racing_slow(self, ir):
        self.copy_standards(ir)
        if ir['CarIdxLapDistPct'][self.carIdx] == -1:
            self.state= "OUT"
            self.processState = CarState.OUT
            return
        self.copy_when_racing(ir)
        if ir['CarIdxOnPitRoad'][self.carIdx]:
            self.state = "PIT"
            self.pitstops += 1
            self.processState = CarState.PIT
            self.pit_boundaries.process_entry(ir['CarIdxLapDistPct'][self.carIdx])


    def state_pitting(self, ir):
        self.copy_standards(ir)
        if ir['CarIdxLapDistPct'][self.carIdx] == -1:
            self.state= "OUT"
            self.processState = CarState.OUT
            return
        self.copy_when_racing(ir)
        if ir['CarIdxOnPitRoad'][self.carIdx] == 0:
            self.state = "RUN"
            self.stintLap = 1
            self.processState = CarState.RUN
            self.pit_boundaries.process_exit(ir['CarIdxLapDistPct'][self.carIdx])

    def state_finished(self, ir):
        # self.logger.debug(f"carIdx {self.carIdx} finished the race.")
        self.copy_standards(ir)

    def state_out_of_race(self, ir):
        self.copy_standards(ir)
        # this may happen after resets or tow to pit road. if not on the pit road it may just be a short connection issue.
        if ir['CarIdxOnPitRoad'][self.carIdx]:
            self.state = "PIT"
            self.processState = CarState.PIT
        else:
            if ir['CarIdxLapDistPct'][self.carIdx] > -1:
                self.state = "RUN"
                self.processState = CarState.RUN

    def process(self, ir):
        # handle processing depending on current state
        self.stateSwitch[self.processState](ir)


    #
    # handle post processing after times, speed, delta are computed
    #

    def state_post_process_noop(self, msg_proc=None):
        pass # do nothing by design

    def state_post_process_run(self, msg_proc):
        if self.speed > 0 and self.speed < CAR_SLOW_SPEED :
            self.state = 'SLOW'
            self.processState = CarState.SLOW
            msg_proc.add_car_slow(self.carIdx,self.speed)

    def state_post_process_slow(self, msg_proc):
        if self.speed > CAR_SLOW_SPEED:
            if self.processState == CarState.SLOW:
                self.processState = CarState.RUN
                self.state = 'RUN'
            else:
                self.logger.warn(f"should not happen. carNum {self.driver_proc.car_number(self.carIdx)} procState: {self.processState} state: {self.state}")




    def post_process(self, msg_proc):
        # handles post processing of special cases.
        self.postProcessStateSwitch[self.processState](msg_proc)



    def copy_standards(self,ir):
        self.carNum = self.driver_proc.car_number(self.carIdx)
        self.userName = self.driver_proc.user_name(self.carIdx)
        self.teamName = self.driver_proc.team_name(self.carIdx)
        self.carClass = self.driver_proc.car_class(self.carIdx)
        self.car = self.driver_proc.car(self.carIdx)

    def copy_when_racing(self, ir):
        self.trackPos = gate(ir['CarIdxLapDistPct'][self.carIdx])
        self.pos = ir['CarIdxPosition'][self.carIdx]
        self.pic = ir['CarIdxClassPosition'][self.carIdx]
        self.lap = ir['CarIdxLap'][self.carIdx]
        self.lc = ir['CarIdxLapCompleted'][self.carIdx]
        self.dist = 0
        self.interval = 0

    def manifest_output(self):
        return [self.__getattribute__(x) for x in self.manifest]
