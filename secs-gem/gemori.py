import logging
import code

import secsgem.common
import secsgem.gem
import secsgem.hsms

from src.utils.gem_logger import CommunicationLogFileHandler


class SampleHost(secsgem.gem.GemHostHandler):
    def __init__(self, settings: secsgem.common.Settings):
        super().__init__(settings)
        self.equipment_name = "001"
        self.MDLN = "gemhost"
        self.SOFTREV = "1.0.0"

    def _on_s06f11(self, handler, message):

        ceid = self.settings.streams_functions.decode(message).CEID
        print("CEID", ceid.get())

        if ceid.get() == 20:
            rsp = self.send_and_waitfor_response(
                self.stream_function(2, 13)([81]))
            s2f14 = self.settings.streams_functions.decode(rsp)
            print("S2F14", s2f14)

        self.send_response(self.stream_function(6, 12)(
            secsgem.secs.data_items.ACKC6.ACCEPTED), message.header.system)


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
