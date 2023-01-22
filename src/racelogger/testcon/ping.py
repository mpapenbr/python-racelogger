import asyncio
import ssl

import certifi
import txaio
from autobahn.asyncio.wamp import ApplicationRunner
from autobahn.asyncio.wamp import ApplicationSession

from racelogger.util.versioncheck import check_server_version


class PingSession(ApplicationSession):

    def onConnect(self):
        self.log.info("Client connecting.")
        self.join(self.config.realm)

    async def onJoin(self, details):
        self.log.info("Connected. Get version")
        try:
            version_info = await self.call("racelog.public.get_version")
            self.log.info(f"Backend service-manager responds with version: {version_info['ownVersion']}")
            self.log.info(f"Compatible with this racelogger version: {check_server_version(version_info['ownVersion'])}")

        except Exception as e:

            self.log.error("Got exception {e}", e=e)
        self.leave()

    def onLeave(self, details):
        self.log.info("Router session closed")
        self.disconnect()

    def onDisconnect(self):
        self.log.info("Router connection closed")
        asyncio.get_event_loop().stop()


def ping(url: str = None, realm: str = None, logLevel: str = 'info', extra=None):

    txaio.start_logging(level=logLevel)
    # we need this for letsencrypt certs.
    # see https://community.letsencrypt.org/t/help-thread-for-dst-root-ca-x3-expiration-september-2021/149190/1213
    if url.startswith("wss://"):
        ssl_context = ssl.create_default_context(cafile=certifi.where())
    else:
        ssl_context = None
    runner = ApplicationRunner(url=url, realm=realm, extra=extra, ssl=ssl_context)
    runner.run(PingSession)
