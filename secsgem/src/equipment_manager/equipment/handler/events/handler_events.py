import threading
import logging
import time
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.secs.dataitems import ACKC6, ACKC5
from secsgem.hsms.packets import HsmsPacket

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.equipment_manager.equipment.equipment import Equipment

logger = logging.getLogger("app_logger")


class EventsCallbacks:
    """
    Class to handle stream functions
    """

    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment

    def _on_s06f11(self, handler, packet: HsmsPacket):
        """
        Handle S6F11
        """
        self.equipment.send_response(self.equipment.stream_function(6, 12)(
            ACKC6.ACCEPTED), packet.header.system)

        decode = self.equipment.secs_decode(packet)
        logger.info("Receive S6F11. %s: %s",
                    self.equipment.equipment_name, decode.get())

        for rpt in decode.RPT:
            if rpt:
                logger.info("RPT: %s", rpt.get())
                rptid = rpt.RPTID
                values = rpt.V
                lot_id, ppname = values
                if rptid.get() == 1000:
                    print("Lot validate: ", lot_id.get())
                    self.equipment.fc_control.fcl.accept_lot(lot_id.get())
                elif rptid.get() == 1001:
                    print("Lot open: ", lot_id.get())
                elif rptid.get() == 1002:
                    print("Lot closed: ", lot_id.get())

        # if self.equipment.equipment_model == "FCL":
        #     # HandlerEventFcl.handle_s6f11(self, handler, packet)
        #     self.event_fcl.handle_s6f11(handler, packet)
        # elif self.equipment_model == "FCLX":
        #     # HandlerEventFclx.handle_s6f11(self, handler, packet)
        #     self.event_fclx.handle_s6f11(handler, packet)
        # else:
        #     logger.warning("Unknown equipment model for %s",
        #                    self.equipment_model)
        #     decode = self.secs_decode(packet)
        #     logger.info("Receive S6F11. %s", self.equipment_name)
        #     logger.info("Receive terminal S6F11: %s", decode.get())
