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


class AlarmCallbacks:
    """
    Class to handle stream functions
    """

    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment

    def _on_s05f01(self, handler, packet: HsmsPacket):
        """
        Handle S5F1
        """

        # first response
        self.equipment.send_response(self.equipment.stream_function(5, 2)(
            ACKC5.ACCEPTED), packet.header.system)

        s5f1 = self.equipment.secs_decode(packet)
        alid = s5f1.ALID.get()
        alcd = s5f1.ALCD.get()
        altx = s5f1.ALTX.get().strip()

        # define vid for FCL and FCLX
        vid = {'FCL': [82, 33], 'FCLX': [3081, 7]}

        _model = self.equipment.equipment_model
        if _model in ['FCL', 'FCLX']:
            _vid = vid[_model]
            # Get PPName and Lot on operate
            s2f4 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 3)(_vid))
            decode_s2f4 = self.equipment.secs_decode(s2f4)

            lot_id, ppname = decode_s2f4
            logger.info("Receive S5F1. %s", self.equipment.equipment_name)

            topic = f"equipments/status/alarm/{self.equipment.equipment_name}"
            message = {
                "ppname": ppname.get(),
                "lot_id": lot_id.get(),
                "alid": alid,
                "alcd": alcd,
                "altx": altx
            }
            self.equipment.mqtt_client.client.publish(topic, str(message))
            # if _model == "FCL":
            #     # handle alarm for FCL
            #     self.alarm_fcl.handle_alarm_fcl(
            #         ppname.get(), lot_id.get(), alid, alcd, altx)
            # elif _model == "FCLX":
            #     # handle alarm for FCLX
            #     self.alarm_fclx.handle_alarm_fclx(
            #         ppname.get(), lot_id.get(), alid, alcd, altx)
        else:
            logger.warning("Unknown equipment model for %s",
                           self.equipment.equipment_model)
            decode = self.equipment.secs_decode(packet)
            logger.info("Receive S5F1. %s", self.equipment.equipment_name)
            logger.info("Receive terminal S5F1: %s", decode.get())
