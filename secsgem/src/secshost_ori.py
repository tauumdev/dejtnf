import logging
import code

import secsgem.common
import secsgem.gem
import secsgem.hsms

from utils.secsgem_logging import CommunicationLogFileHandler


class SampleHost(secsgem.gem.GemHostHandler):
    def __init__(self, settings: secsgem.common.Settings):
        super().__init__(settings)

        self.MDLN = "gemhost"
        self.SOFTREV = "1.0.0"


commLogFileHandler = CommunicationLogFileHandler("logs", "h")
commLogFileHandler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
logging.getLogger("communication").addHandler(commLogFileHandler)
logging.getLogger("communication").propagate = False

logging.basicConfig(
    format='%(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.DEBUG)

settings = secsgem.hsms.HsmsSettings(
    address="192.168.226.161",
    port=5000,
    session_id=61,
    connect_mode=secsgem.hsms.HsmsConnectMode.ACTIVE,
    device_type=secsgem.common.DeviceType.HOST
)

h = SampleHost(settings)
h.enable()

code.interact("host object is available as variable 'h'", local=locals())

h.disable()
