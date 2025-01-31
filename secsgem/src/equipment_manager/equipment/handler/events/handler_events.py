import threading
import logging
import time
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.secs.dataitems import ACKC6, ACKC5
from secsgem.hsms.packets import HsmsPacket
from src.equipment_manager.equipment.handler.events.fclx.fclx import HandlerEventFCLX
from src.equipment_manager.equipment.handler.events.fcl.fcl import HandlerEventFCL


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
        self.fcl_handler = HandlerEventFCL(equipment)  # Create instance
        self.fclx_handler = HandlerEventFCLX(equipment)  # Create instance

    def _on_s06f11(self, handler, packet: HsmsPacket):
        """
        Handle S6F11
        """
        self.equipment.send_response(self.equipment.stream_function(6, 12)(
            ACKC6.ACCEPTED), packet.header.system)

        # handle by equipment model
        model = self.equipment.equipment_model
        if model == "FCL":
            self.fcl_handler.s06f11(handler, packet)
        elif model == "FCLX":
            self.fclx_handler.s06f11(handler, packet)
        else:
            print(f"Other Model: {self.equipment.equipment_name, model}")
