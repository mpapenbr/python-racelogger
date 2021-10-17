import logging
import time
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from os import system
from typing import Callable

import irsdk

from racelogger.model.recorderstate import RecorderState
from racelogger.processing.carproc import CarProcessor
from racelogger.processing.driverproc import DriverProcessor
from racelogger.processing.msgproc import MessageProcessor
from racelogger.processing.subprocessors import Subprocessors


class RaceStates(Enum):
    INVALID = 0
    RACING = 1
    CHECKERED_ISSUED = 2
    CHECKERED_DONE = 3
    COOLDOWN = 4
    TERMINATE = 5

@dataclass
class RaceProcessor:
    """state machine which is triggered on every iteration of the main loop"""
    recorderState: RecorderState
    """holds the data from iRacing"""
    subprocessors: Subprocessors
    """container for subprocessors"""
    state: RaceStates = RaceStates.INVALID
    """holds the current state of the race"""
    session_unique_id: int = -1
    """holds the current session unique id"""
    session_num: int = -1
    """holds the current session num (uses for resets and the like during testing)"""
    onNewSession: Callable[[int],None] = None
    """if present this will be called if a new session num is detected"""

    def __post_init__(self):
        self.on_init_ir_state = self.recorderState.ir['SessionState'] # used for "race starts" message
        self.stateSwitch = {
            RaceStates.INVALID: self.state_invalid,
            RaceStates.RACING: self.state_racing,
            RaceStates.CHECKERED_ISSUED: self.state_finishing,
            RaceStates.CHECKERED_DONE: self.state_racing,
            RaceStates.COOLDOWN: self.state_cooldown,
            RaceStates.TERMINATE: self.state_terminate,
        }
        self.logger = logging.getLogger("RaceProcessor")


    def state_invalid(self,ir):
        if ir['SessionInfo']['Sessions'][ir['SessionNum']]['SessionType'] == 'Race':
            if ir['SessionState'] == irsdk.SessionState.racing:
                self.logger.info(f'=== Race state detected ===')
                # self.pit_proc.race_starts(ir)
                self.subprocessors.car_proc.race_starts(ir)
                self.state = RaceStates.RACING
                if self.on_init_ir_state != ir['SessionState']:
                    self.logger.info(f'real race start detected')
                    self.subprocessors.msg_proc.add_race_starts()
                    pass

    def state_racing(self,ir):
        if ir['SessionState'] == irsdk.SessionState.checkered:
            self.logger.info(f'checkered flag issued')
            self.state = RaceStates.CHECKERED_ISSUED
            self.subprocessors.car_proc.checkered_flag(ir)
            self.subprocessors.msg_proc.add_checkered_issued()
            # need to check where the leader is now. has he already crossed s/f ?
            # (problem is a about to be lapped car in front of that car - which of course should not yet be considered as a finisher)
            return

        # TODO: do we still need pit_process???
        # self.pit_proc.process(ir)

        # state.driver_proc.process(ir)
        self.subprocessors.car_proc.process(ir, self.subprocessors.msg_proc)

    def state_finishing(self,ir):
        if ir['SessionState'] == irsdk.SessionState.cool_down:
            # TODO: at this point the last car may not be processed in the standings. check when time
            # idea: separate into two state: cooldown_issued. after  5s  all missing data should be processed. After that terminate.
            self.subprocessors.car_proc.process(ir, self.subprocessors.msg_proc)
            self.logger.info(f'cooldown signaled - get out of here')
            self.state = RaceStates.COOLDOWN
            self.cooldown_signaled = time.time()
            return

        # self.subprocessors.pit_proc.process(ir)
        self.subprocessors.car_proc.process(ir, self.subprocessors.msg_proc)

    def state_cooldown(self, ir):
        """
        on cooldown notice we want to stay 5 more secs active to get the latest standings.
        """
        if (time.time() - self.cooldown_signaled) < 5:
            self.subprocessors.car_proc.process(ir, self.subprocessors.msg_proc)
            return
        else:
            self.logger.info(f'internal cooldown phase done. Terminating now')
            self.state = RaceStates.TERMINATE
            return

    def state_terminate(self, ir ):
        # TODO: think about shutting down only when specific config attribute is set to do so ;)
        # for now it is ok.
        self.logger.info(f'unregister service')
        # unregister_service()
        self.logger.info(f'unregister called')
        system.exit(0)
        self.logger.error(f'should not see this')

    def handle_new_session(self,ir):
        self.subprocessors.msg_proc.clear_buffer()

        # self.subprocessors.pit_proc.clear_buffer()
        # state.car_proc.clear_buffer()
        self.session_num = ir['SessionNum']
        self.session_unique_id = ir['SessionUniqueID']

        self.state = RaceStates.INVALID
        self.on_init_ir_state = ir['SessionState'] # used for "race starts" message
        # state.last_data.speedmap = SpeedMap(state.track_length)
        self.logger.info(f'new unique session detected: {self.session_unique_id} sessionNum: {self.session_num}')
        if self.onNewSession:
            self.onNewSession(self.session_num)

    def process(self, ir):
        """processes one step on the state machine according to the data in recorderState.ir"""
        # handle global changes here
        if ir['SessionUniqueID'] != 0 and ir['SessionUniqueID'] != self.session_unique_id:
            self.handle_new_session(ir)
        # handle processing depending on current state
        self.stateSwitch[self.state](ir)
