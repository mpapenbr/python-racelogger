

from racelogger.processing.driverproc import DriverProcessor

MessagesManifest = ['type', 'subType', 'carIdx','carNum', 'carClass', 'msg']

class MessageProcessor:
    def __init__(self, driver_proc:DriverProcessor) -> None:
        self.msg_buffer = []
        self.driver_proc = driver_proc

    def clear_buffer(self):
        self.msg_buffer.clear()

    def add_pit_enter_msg(self, pitinfo):
        self.msg_buffer.append({
            'type': 'Pits',
            'subType':'Enter',
            'carIdx': pitinfo.car_idx,
            'carNum': self.driver_proc.car_number(pitinfo.car_idx),
            'carClass': self.driver_proc.car_class(pitinfo.car_idx),
            'msg': f'#{self.driver_proc.car_number(pitinfo.car_idx)} ({self.driver_proc.user_name(pitinfo.car_idx)}) entered pitlane'})

    def add_pit_exit_msg(self, pitinfo):
        self.msg_buffer.append({
            'type': 'Pits',
            'subType':'Exit',
            'carIdx': pitinfo.car_idx,
            'carNum': self.driver_proc.car_number(pitinfo.car_idx),
            'carClass': self.driver_proc.car_class(pitinfo.car_idx),
            'msg': f'#{self.driver_proc.car_number(pitinfo.car_idx)} ({self.driver_proc.user_name(pitinfo.car_idx)}) exited pitlane'})

    def add_driver_enter_car(self, car_idx):
        self.msg_buffer.append({
            'type': 'Pits',
            'subType':'Driver',
            'carIdx': car_idx,
            'carNum': self.driver_proc.car_number(car_idx),
            'carClass': self.driver_proc.car_class(car_idx),
            'msg': f'#{self.driver_proc.car_number(car_idx)} ({self.driver_proc.user_name(car_idx)}) entered car'})

    def add_car_slow(self, car_idx, speed):
        self.msg_buffer.append({
            'type': 'Track',
            'subType':'Driver',
            'carIdx': car_idx,
            'carNum': self.driver_proc.car_number(car_idx),
            'carClass': self.driver_proc.car_class(car_idx),
            'msg': f'#{self.driver_proc.car_number(car_idx)} ({self.driver_proc.user_name(car_idx)}) car slow ({speed})'})

    def add_timing_info(self, car_idx, msg):
        self.msg_buffer.append({
            'type': 'Timing',
            'subType':'Driver',
            'carIdx': car_idx,
            'carNum': self.driver_proc.car_number(car_idx),
            'carClass': self.driver_proc.car_class(car_idx),
            'msg': f'#{self.driver_proc.car_number(car_idx)} ({self.driver_proc.user_name(car_idx)}) {msg}'})


    def add_race_starts(self):
        self.msg_buffer.append({
            'type': 'Timing',
            'subType':'RaceControl',
            'carIdx': None,
            'carNum': None,
            'carClass': None,
            'msg': f'Race start'})

    def add_checkered_issued(self):
        self.msg_buffer.append({
            'type': 'Timing',
            'subType':'RaceControl',
            'carIdx': None,
            'carNum': None,
            'carClass': None,
            'msg': f'Checkered flag'})

    def manifest_output(self):
        return [[m[x] for x in MessagesManifest] for m in self.msg_buffer]
