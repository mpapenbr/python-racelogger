import logging
import sys
import time
import traceback
from dataclasses import dataclass
from dataclasses import field
from typing import Callable

from racelogger.model.messages import Message
from racelogger.model.messages import MessageType
from racelogger.model.messages import StateMessage
from racelogger.model.recorderstate import RecorderState
from racelogger.processing.raceproc import RaceProcessor
from racelogger.processing.session import SessionData
from racelogger.processing.subprocessors import Subprocessors


@dataclass
class Processor:
    """handles the processing of data from iRacing telemetry"""
    state: RecorderState
    """holds the current recorder state"""
    raceProcessor: RaceProcessor
    """is responsible for processing the current iracing data"""
    subprocessors: Subprocessors
    """container with subprocessors"""
    state_publisher: Callable[[any], None]
    """is called when state data should be send to server"""
    cardata_publisher: Callable[[any], None]
    """is called when driver data should be send to server"""
    speedmap_publisher: Callable[[any], None]
    """is called when speedmap data should be send to server"""
    speedmap_publish_interval: int = field(init=True, default=60)
    """interval in seconds to publish the speedmap"""

    driver_initial_published: bool = field(init=False, default=False)
    """will be set to to true once the initial driver data is sent to the server"""
    stateLastPublished: float = field(init=False, default=0.0)
    """contains the sessionTime when the state data was published"""
    speedmapLastPublished: float = field(init=False, default=0.0)
    """contains the sessionTime when the speedmap data was published"""
    lastDI: any = field(init=False, default=None)
    """contains the last updated ir['DriverInfo'] data"""

    def __post_init__(self):
        self.log = logging.getLogger("MainProcessor")
        self.raceProcessor.onNewSession = self.postProcessNewSession

    def isConnected(self) -> bool:
        return self.state.ir.is_connected

    def step(self) -> float:
        """processes one iteration of the loop. assumes to be called if the connection still exists"""
        mark = time.time()
        self.state.ir.freeze_var_buffer_latest()
        ownProcessingStart = time.time()
        curSessionTime = self.state.ir['SessionTime']
        if curSessionTime == 0.0:
            # there are race situatione where the whole ir-Data are filled with 0 bytes. Get out of here imediately
            #logger.warning("Possible invalid data in ir - session time is 0.0. skipping loop")
            return time.time() - mark

        try:
            if self.state.ir['DriverInfo']:
                if self.state.ir['DriverInfo'] != self.lastDI:
                    self.lastDI = self.state.ir['DriverInfo']
                    self.subprocessors.driver_proc.process(self.state.ir, self.subprocessors.msg_proc)
                    self.publishCarData()
            # do the processing here
            self.raceProcessor.process(self.state.ir)

            if (curSessionTime - self.stateLastPublished) > 1:
                self.publishState()
                self.stateLastPublished = curSessionTime

            if (curSessionTime - self.speedmapLastPublished) > self.speedmap_publish_interval:
                self.publishSpeedmapData()
                self.speedmapLastPublished = curSessionTime

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            self.log.error(f"Some other exception: {e=}")
        ownDuration = time.time() - ownProcessingStart
        duration = time.time()-mark
        # self.log.debug(f"{ownDuration=} {duration=}")
        return duration

    def postProcessNewSession(self, newSessionNum: int):
        self.log.debug(f"postProcessNewSession called with {newSessionNum}")
        self.stateLastPublished = 0

    def publishState(self):
        sessionData = SessionData(self.state.ir)
        messages = self.subprocessors.msg_proc.manifest_output()
        cars = self.subprocessors.car_proc.manifest_output()
        # pits = state.pit_proc.manifest_output()
        stateMsg = StateMessage(session=sessionData.manifest_output(), messages=messages, cars=cars, pits=[])
        msg = Message(type=MessageType.STATE.value, payload=stateMsg.__dict__)
        # self.log.debug(f"about to publish state data {msg.__dict__}")
        self.state_publisher(msg.__dict__)
        self.subprocessors.msg_proc.clear_buffer()

    def publishCarData(self):
        self.log.debug(f"about to publish car data")
        msg = Message(type=MessageType.CAR.value, payload=self.subprocessors.driver_proc.driverdata_output())
        self.cardata_publisher(msg.__dict__)

    def publishSpeedmapData(self):
        self.log.debug(f"about to publish speedmap data")
        msg = Message(type=MessageType.SPEEDMAP.value, payload=self.subprocessors.car_proc.speedmap_output(self.state.ir))
        self.speedmap_publisher(msg.__dict__)
