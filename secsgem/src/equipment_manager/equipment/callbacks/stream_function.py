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


class RegisterCallbacks:
    """
    Class to handle stream functions
    """

    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment

    def s01f13(self, handler, packet: HsmsPacket):
        """
        Handle S1F13
        """
        logger.info("Receive S1F13. %s", self.equipment.equipment_name)
        pass

    def s01f14(self, handler, packet: HsmsPacket):
        """
        Handle S1F14
        """
        logger.info("Receive S1F14. %s", self.equipment.equipment_name)
        pass

    def s09f1(self, handle, packet):
        logger.warning("s09f1:Unrecognized Device ID (UDN): %s",
                       self.equipment.equipment_name)

    def s09f3(self, handle, packet):
        logger.warning("s09f3:Unrecognized Stream Function (SFCD): %s",
                       self.equipment.equipment_name)

    def s09f5(self, handle, packet):
        logger.warning("s09f5:Unrecognized Function Type (UFN): %s",
                       self.equipment.equipment_name)

    def s09f7(self, handle, packet):
        logger.warning("s09f7:Illegal Data (IDN): %s",
                       self.equipment.equipment_name)

    def s09f9(self, handle, packet):
        logger.warning("s09f9:Transaction Timer Timeout (TTN): %s",
                       self.equipment.equipment_name)

    def s09f11(self, handle, packet):
        logger.warning("s09f11:Data Too Long (DLN): %s",
                       self.equipment.equipment_name)
