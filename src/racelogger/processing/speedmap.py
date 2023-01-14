import argparse
import logging
import logging.config
import math
import time
from functools import reduce

import irsdk
import yaml


class ChunkData:
    """
    @param keep_hist use at most this many entries for computation

    @param min_hist build up at least this many entries before deciding about which entries to keep.
    """

    def __init__(self, id, keep_hist=11, min_hist=3) -> None:
        self.id = id
        self.min = 0
        self.max = 0
        self.avg = 0
        self.hist = []
        self.keep_hist = keep_hist
        self.min_hist = min_hist

    def process(self, speed):
        """
        process the given speed. This method also decides whether the speed should be used for further computation
        """
        if len(self.hist) < self.keep_hist:
            self.hist.append(speed)
            self.recompute_values()
            return
        self.hist.append(speed)
        if len(self.hist) % 2 == 1:
            self.hist.sort()
            self.hist = self.hist[1:-1]
        self.recompute_values()

    def process_with_reference_data(self, speed, reference_data):
        """
        process the given speed. This method also decides wheter the speed should be used for further computation
        """
        if len(self.hist) < self.min_hist:
            self.hist.append(speed)
            self.recompute_values()
            return
        # now we have to decide what to do with the new value

    def recompute_values(self):
        """
        docstring
        """
        self.min = min(self.hist)
        self.max = max(self.hist)
        self.avg = sum(self.hist)/len(self.hist)

    def __repr__(self) -> str:
        tmp = ", ".join([f"{e:.0f}" for e in self.hist])
        return f'ChunkData {self.id}: min: {self.min:3.0f} max: {self.max:3.0f} avg: {self.avg:3.0f} hist: {tmp}'


class SpeedMap:
    """
    tracks the speed of car classes and single cars on different chunks of the track.
    This data is used for computing the intervals (in s) between cars
    """

    def __init__(self, track_length, chunk_size=10):
        """
        @param track_length: the track length (meters)

        @param chunk_size: the size of each chunk (meters)

        @param car_classes: the number of car_classes to monitor
        """
        self.track_length = track_length
        self.chunk_size = chunk_size
        self.num_chunks = math.ceil(self.track_length / self.chunk_size)
        self.track_pos = 0
        self.logger = logging.getLogger(self.__class__.__name__)
        self.datalogger = logging.getLogger(self.__class__.__name__ + 'Data')
        self.computelogger = logging.getLogger(self.__class__.__name__ + 'Compute')
        self.__create_chunks()

    def __repr__(self) -> str:
        return f'SpeedMap trackLength: {self.track_length} chunkSize: {self.chunk_size}'

    def __create_chunk(self):
        def init_chunk_data(): return [ChunkData(y) for y in range(self.num_chunks)]
        return init_chunk_data()

    def __create_chunks(self):
        self.logger.debug(f"Initializing chunk data")
        self.car_classes_dict = {}
        self.car_idx_chunks = [self.__create_chunk() for i in range(64)]

    def __delta_distance(a, b):
        if a > b:
            return a-b
        else:
            return 1-b+a

    def __get_chunk_idx(self, track_pos_pct):
        # in rare cases the track_pos_pct gets a little bit over 1. In such cases we put it back at the start
        if track_pos_pct > 1:
            return 0
        else:
            idx = math.floor(track_pos_pct * self.track_length / self.chunk_size)
            # safeguard: sometimes we get track_pos_pct of 1.0 which would exceed the chunks. In such cases we take the last chunk.
            if idx >= self.num_chunks:
                return idx-1
            return idx

    def process(self, track_pos, speed, car_class_id):
        self.track_pos = track_pos
        chunk_idx = self.__get_chunk_idx(track_pos)
        car_class_chunks = self.car_classes_dict.get(car_class_id)
        if car_class_chunks == None:
            car_class_chunks = self.__create_chunk()
            self.car_classes_dict[car_class_id] = car_class_chunks
        car_class_chunks[chunk_idx].process(speed)

    def compute_delta_time(self, car_class_id, pct_car_in_front, pct_current_car):

        chunk_idx_car_in_front = self.__get_chunk_idx(pct_car_in_front)
        chunk_idx_current_car = self.__get_chunk_idx(pct_current_car)

        car_class_chunks = self.car_classes_dict.get(car_class_id)
        if (car_class_chunks == None):
            self.logger.warn(f'No chunk_data for carClassId {car_class_id} available. return -1')
            return -1
        chunk_data = []
        if (chunk_idx_car_in_front < chunk_idx_current_car):
            #  we need [0:chunk_idx_car_in_front+1] and [chunk_idx_current_car:]
            chunk_data.extend(car_class_chunks[chunk_idx_current_car:])
            chunk_data.extend(car_class_chunks[0:chunk_idx_car_in_front+1])
        else:
            # we need [chunk_idx_current_car:chunk_idx_car_in_front+1]
            chunk_data.extend(car_class_chunks[chunk_idx_current_car:chunk_idx_car_in_front+1])
        self.computelogger.debug(f"chunk_idx_car_in_front: {chunk_idx_car_in_front}  chunk_idx_current_car: {chunk_idx_current_car}")
        # do nothing if we dont have averages in chunks
        if len(chunk_data) == 0:
            return 0
        if any(d.avg == 0 for d in chunk_data):
            return 0
        # for the first item: calculate the time from pct_current_car to end of chunk
        meters_to_end_of_chunk = (chunk_idx_current_car+1)*self.chunk_size-(pct_current_car*self.track_length)
        delta = meters_to_end_of_chunk / chunk_data[0].avg * 3.6
        total_delta = delta
        self.computelogger.debug(f"first: meters: {meters_to_end_of_chunk} avg: {chunk_data[0].avg:.0f} delta: {delta}")

        for c in chunk_data[1:-1]:
            delta = self.chunk_size / c.avg * 3.6
            self.computelogger.debug(f"middle: meters: {self.chunk_size} avg: {c.avg:.0f} delta: {delta}")
            total_delta += delta

        # for the last item: calculate the time from begin of chunk to pct_car_in_front
        meters_from_start_of_chunk = (pct_car_in_front*self.track_length)-(chunk_idx_car_in_front)*self.chunk_size
        delta = meters_from_start_of_chunk / chunk_data[-1].avg * 3.6

        self.computelogger.debug(f"end: meters: {meters_from_start_of_chunk} avg: {chunk_data[-1].avg:.0f} delta: {delta}")

        total_delta += delta

        return total_delta

    def output_data(self, session_time: float, track_temp: float, time_of_day: float) -> dict:
        def compute_laptime(chunks) -> float:
            """computes the laptime of a lap by computing the time needed for each chunk (speed is given in km/h)"""
            # if there are still unvisited chunks, skip laptime calulation
            try:
                chunks.index(0)
                return 0
            except ValueError:
                ret: float = reduce(lambda prev, cur: prev + self.chunk_size / (cur / 3.6), chunks, 0)
                return ret

        ret = {
            'sessionTime': session_time,
            'timeOfDay': time_of_day,
            'trackTemp': track_temp,
            'trackLength': self.track_length,
            'chunkSize': self.chunk_size,
            'currentPos': self.track_pos,
            'data': {k: {'chunkSpeeds': [lv.avg for lv in v],
                         'laptime': compute_laptime([lv.avg for lv in v])} for k, v in self.car_classes_dict.items()},
        }
        return ret

    def log_car_classes(self):
        """
        docstring
        """
        if (self.datalogger.isEnabledFor(logging.DEBUG)):
            for k, v in self.car_classes_dict.items():
                # for item in sorted(self.car_classes_dict.values(), key=lambda x: id):
                for chunk in v:
                    self.datalogger.debug(f'ClassId: {k}: {chunk}')


# info: https://realpython.com/python-logging/
if __name__ == '__main__':
    with open('logging.yaml', 'r') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    sm = SpeedMap(track_length=4000, chunk_size=1000)
    # sm.process(0.11, 200, 1, 289)
    # sm.process(0.41, 150, 2, 289)
    # sm.process(0.52, 100, 3, 289)
    # sm.process(0.88, 250, 3, 289)
    sm.process(0.11, 50, 3, 289)
    sm.process(0.11, 150, 3, 289)
    sm.process(0.11, 200, 3, 289)
    sm.process(0.11, 250, 3, 289)
    sm.process(0.11, 175, 3, 289)

    sm.log_car_classes()
    # print(sm.compute_delta_time(289, 0.45, 0.11))
    # print(sm.compute_delta_time(289, 0.11, 0.45))
    # print(sm.compute_delta_time(289, 0.24, 0.01))
    # print(sm.compute_delta_time(289, 0.01, 0.98))
    #print(sm.compute_delta_time(289, 0.99, 0.01))
