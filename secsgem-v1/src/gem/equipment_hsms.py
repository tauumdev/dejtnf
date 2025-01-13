import logging
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.secs.dataitems import ACKC6
from secsgem.hsms.packets import HsmsPacket

logger = logging.getLogger("app_logger")


class Equipment(secsgem.gem.GemHostHandler):
    def __init__(self, address, port: int, active: bool, session_id: int, name: str, equipment_model: str, is_enable: bool, custom_connection_handler=None):
        super().__init__(address, port, active, session_id, name, custom_connection_handler)
        self.equipment_name = name
        self.equipment_model = equipment_model
        self.MDLN = "dejtnf"
        self.SOFTREV = "1.0.1"
        self.is_enabled = is_enable

        self.register_stream_function(1, 14, self.s01f14)

    def _on_state_communicating(self, _):
        current_state = self.communicationState.current
        logger.info("%s Communication state: %s",
                    self.equipment_name, current_state)
        return super()._on_state_communicating(_)

    def _on_state_disconnect(self):
        current_state = self.communicationState.current
        logger.info("%s Communication state: %s",
                    self.equipment_name, current_state)
        return super()._on_state_disconnect()

    def on_connection_closed(self, connection):
        current_state = self.communicationState.current
        logger.info("%s Communication state: %s",
                    self.equipment_name, current_state)
        return super().on_connection_closed(connection)

    def s01f14(self, handler, packet: HsmsPacket):
        logger.info("S01F14")

    def _on_s06f11(self, handler, packet: HsmsPacket):
        self.send_response(self.stream_function(6, 12)(
            ACKC6.ACCEPTED), packet.header.system)

        decode = self.secs_decode(packet)
        ceid = decode.CEID
        if ceid == 20:
            # print(decode.CEID.get())
            self.send_remote_command(
                rcmd="LOT_ACCEPT", params=[["LotID", "123456"]])
