import asyncio
import hashlib
import logging
import ssl
import time
from logging import config

import certifi
import irsdk
import txaio
from autobahn.asyncio.wamp import ApplicationRunner
from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
from autobahn.wamp.types import PublishOptions
from autobahn.wamp.types import RegisterOptions

from racelogger.model.recorderstate import RecorderState
from racelogger.processing.carproc import CarProcessor
from racelogger.processing.driverproc import DriverProcessor
from racelogger.processing.msgproc import MessageProcessor
from racelogger.processing.msgproc import MessagesManifest
from racelogger.processing.processor import Processor
from racelogger.processing.raceproc import RaceProcessor
from racelogger.processing.session import SessionManifest
from racelogger.processing.subprocessors import Subprocessors
from racelogger.util.utils import collect_event_info
from racelogger.util.utils import collect_track_info


class RecordingSession(ApplicationSession):
    """
    main class to manage the recording of race data from iRacing telemetry.
    """

    def onConnect(self):
        self.log.info("Client connected: {klass}", klass=ApplicationSession)
        self.join(self.config.realm, authid=self.config.extra['user'], authmethods=["ticket"])

    def onChallenge(self, challenge):
        self.log.info("Challenge for method {authmethod} received", authmethod=challenge.method)
        return self.config.extra['password']

    async def onJoin(self, details):
        state = await self._wait_for_iracing()
        self.log.info(f"state is {state}")

        await self.recordingLoop(state)
        self.log.info("after recordingLoop")
        self.leave()

    async def registerEvent(self, state: RecorderState, car_proc: CarProcessor):
        self.track_info = collect_track_info(state.ir)
        self.event_info = collect_event_info(state.ir,
                                             name=self.config.extra['name'] if 'name' in self.config.extra else None,
                                             description=self.config.extra['description'] if 'description' in self.config.extra else None)
        print(f"{self.track_info=}\n{self.event_info}")
        racelog_event_key = hashlib.md5(state.ir['WeekendInfo'].__repr__().encode('utf-8')).hexdigest()
        state.eventKey = racelog_event_key
        register_data = {
            'eventKey': racelog_event_key,
            'manifests': {
                'car': car_proc.manifest,
                'session': SessionManifest,
                'message': MessagesManifest,
                'pit': []  # TODO: remove if removed in backend (not needed anymore)
            },
            'info': self.event_info,
            'trackInfo': self.track_info
        }
        # TODO: refactor with new backend endpoint
        await self.call("racelog.dataprovider.register_provider", register_data)

    async def unregisterService(self, state: RecorderState, car_proc: CarProcessor):
        """collect pit boundaries from CarProcessor, send update server and remove us as provider"""
        def pit_lane_length(entry: float, exit: float) -> float:
            if exit > entry:
                return (exit-entry) * self.track_info['trackLength']
            else:
                return (1-entry + exit) * self.track_info['trackLength']

        self.track_info['pit'] = {
            'entry': car_proc.pit_boundaries.pit_entry_boundary.middle,
            'exit': car_proc.pit_boundaries.pit_exit_boundary.middle,
            'laneLength': pit_lane_length(
                car_proc.pit_boundaries.pit_entry_boundary.middle,
                car_proc.pit_boundaries.pit_exit_boundary.middle)
        }

        await self.call("racelog.dataprovider.store_event_extra_data", state.eventKey, {'track': self.track_info})
        await self.call("racelog.dataprovider.remove_provider", state.eventKey)

    def stopLoop(self):
        """triggers termination of recording loop"""
        self.shouldRun = False

    async def recordingLoop(self, state: RecorderState):
        self.shouldRun = True

        driver_proc = DriverProcessor(state.ir)
        msg_proc = MessageProcessor(driver_proc)
        car_proc = CarProcessor(driver_proc, state.ir)
        subprocessors = Subprocessors(driver_proc=driver_proc, car_proc=car_proc, msg_proc=msg_proc)
        await self.registerEvent(state, car_proc)
        self.processor = Processor(
            state=state,
            subprocessors=subprocessors,
            raceProcessor=RaceProcessor(recorderState=state, subprocessors=subprocessors),
            state_publisher=lambda data: self.publish(state.publishStateTopic(), data),
            cardata_publisher=lambda data: self.publish(state.publishCarDataTopic(), data),
            speedmap_publisher=lambda data: self.publish(state.publishSpeedmapTopic(), data),
            speedmap_publish_interval=self.config.extra['speedmap_interval']

        )

        self.processor.raceProcessor.onRaceFinished = lambda: self.stopLoop()
        while self.shouldRun and self.processor.state.ir.is_connected:
            try:
                duration = self.processor.step()
                pause = max(0, 1/60-duration)
                await asyncio.sleep(pause)

            except Exception as e:
                self.log.error(f"Some other exception: {e=}")
                pass
        # loop ended. if we get here, the connection or the race is terminated
        self.log.info(f"Processing finished. {self.processor.state.ir_connected=}")
        await self.unregisterService(state, car_proc)

    def onLeave(self, details):
        self.log.info("Router session closed ({details})", details=details)
        self.disconnect()

    def onDisconnect(self):
        self.log.info("Router connection closed")
        asyncio.get_event_loop().stop()

    async def _wait_for_iracing(self):
        self.log.info("Waiting for iRacing")
        ir = irsdk.IRSDK()
        ir.startup()
        state = RecorderState(ir_connected=False, ir=ir)

        while not (ir.is_initialized and ir.is_connected):
            self.log.debug(f"checking iRacing {ir.is_initialized=} {ir.is_connected=}")
            await asyncio.sleep(1)
        self.log.debug("DEBUG-Connected to iRacing")
        self.log.info("Connected to iRacing")
        state.ir_connected = True
        return state


def record(url: str = None, realm: str = None, logLevel: str = 'error', logconfig="logging.conf", extra=None):
    # logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # logging.getLogger('SpeedMapCompute').setLevel(logging.ERROR)
    # logging.getLogger('SpeedMap').setLevel(logging.ERROR)
    txaio.start_logging(level=logLevel)
    config.fileConfig(logconfig)
    # we need this for letsencrypt certs.
    # see https://community.letsencrypt.org/t/help-thread-for-dst-root-ca-x3-expiration-september-2021/149190/1213
    if url.startswith("wss://"):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
    else:
        ssl_context = None
    runner = ApplicationRunner(url=url, realm=realm, extra=extra, ssl=ssl_context)
    runner.run(RecordingSession)
