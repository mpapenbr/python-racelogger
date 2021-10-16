import asyncio
import logging
import ssl
import time

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
from racelogger.processing.processor import Processor
from racelogger.processing.raceproc import RaceProcessor
from racelogger.processing.subprocessors import Subprocessors


class ClientSession(ApplicationSession):

    def onConnect(self):
        self.log.info("Client connected: {klass}", klass=ApplicationSession)
        self.join(self.config.realm, authid=self.config.extra['user'], authmethods=["ticket"])

    def onChallenge(self, challenge):
        self.log.info("Challenge for method {authmethod} received", authmethod=challenge.method)
        return self.config.extra['password']


    async def onJoin(self, details):
        state = await self._wait_for_iracing()
        self.log.info(f"state is {state}")

        await self.demoLoop(state)
        self.log.info("after demoLoop")
        self.disconnect()

    async def demoLoop(self, state:RecorderState):
        self.shouldRun = True
        start = time.time()
        maxtime = self.config.extra['maxtime']
        driver_proc = DriverProcessor(state.ir)
        msg_proc = MessageProcessor(driver_proc)
        car_proc = CarProcessor(driver_proc, state.ir)
        subprocessors = Subprocessors(driver_proc=driver_proc, car_proc=car_proc, msg_proc=msg_proc)
        self.processor = Processor(
            state=state,
            subprocessors=subprocessors,
            raceProcessor=RaceProcessor(recorderState=state,subprocessors=subprocessors),
            publisher=lambda data: self.publish("racelog.racedata.raw", data),
            caller=lambda endpoint,data: self.call(endpoint, data),
            )
        while self.shouldRun and self.processor.state.ir.is_connected:
            try:

                duration = self.processor.step()
                pause = max(0,1/60-duration)
                if 1==0: # by design. may activate if wanted
                    if duration > 1/60:
                        overdue = duration - 1/60
                        self.log.debug(f"{overdue=} {pause=}")
                    else:
                        self.log.debug(f"no overdue, yielding {pause=}")
                await asyncio.sleep(pause)
                if maxtime != None and (time.time() - start > maxtime):
                    self.shouldRun = False
            except Exception as e:
                self.log.error(f"Some other exception: {e=}")
                pass
        # loop ended. if we get here, the connection or the race terminated
        self.log.info(f"Processing finished. {self.processor.state.ir_connected=}")

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
        self.log.info("Connected to iRacing")
        state.ir_connected = True
        return state


def testLoop(url:str=None, realm:str=None, logLevel:str='error', extra=None):
    logging.getLogger('SpeedMapCompute').setLevel(logging.ERROR)
    logging.getLogger('SpeedMap').setLevel(logging.ERROR)
    txaio.start_logging(level=logLevel)
    # we need this for letsencrypt certs.
    # see https://community.letsencrypt.org/t/help-thread-for-dst-root-ca-x3-expiration-september-2021/149190/1213
    if url.startswith("wss://"):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
    else:
        ssl_context = None
    runner = ApplicationRunner(url=url, realm=realm, extra=extra, ssl=ssl_context)
    runner.run(ClientSession)

