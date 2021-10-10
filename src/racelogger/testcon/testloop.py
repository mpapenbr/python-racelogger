import asyncio
import ssl

import certifi
import txaio
from autobahn.asyncio.wamp import ApplicationRunner
from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
from autobahn.wamp.types import PublishOptions
from autobahn.wamp.types import RegisterOptions


class ClientSession(ApplicationSession):
    def onConnect(self):
        self.log.info("Client connected: {klass}", klass=ApplicationSession)
        self.join(self.config.realm, authid=self.config.extra['user'], authmethods=["ticket"])

    def onChallenge(self, challenge):
        self.log.info("Challenge for method {authmethod} received", authmethod=challenge.method)
        return self.config.extra['password']


    async def onJoin(self, details):
        # await self._init_person_api()
        await self.producer()
        self.log.info("after setup producer")

    async def producer(self):
        self.produce = True
        counter = 0
        while self.produce:
            try:
                self.publish(u'racelog.Hallo', counter)
                counter += 1
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                # try:
                #     unregister_service()
                # except:
                #     pass
                # press ctrl+c to exit
                self.log.info("Got interrupted by user. Terminating")
                self.produce = False
            except Exception:
                self.log.info("Some other exception")
                pass

    def onLeave(self, details):
        self.log.info("Router session closed ({details})", details=details)
        self.disconnect()

    def onDisconnect(self):
        self.log.info("Router connection closed")
        asyncio.get_event_loop().stop()

def testLoop(url:str=None, realm:str=None, logLevel:str='error', extra=None):
    txaio.start_logging(level=logLevel)
    # we need this for letsencrypt certs.
    # see https://community.letsencrypt.org/t/help-thread-for-dst-root-ca-x3-expiration-september-2021/149190/1213
    if url.startswith("wss://"):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
    else:
        ssl_context = None
    runner = ApplicationRunner(url=url, realm=realm, extra=extra, ssl=ssl_context)
    runner.run(ClientSession)

