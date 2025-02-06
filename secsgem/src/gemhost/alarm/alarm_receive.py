import logging
from secsgem.hsms.packets import HsmsPacket
from secsgem.secs.dataitems import ACKC5

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gemhost.equipment import Equipment

logger = logging.getLogger("app_logger")


class HandlerAlarmsReceive:
    """
    Class for handling alarms
    """

    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment

    def s05f01(self, handler, packet: HsmsPacket):
        """
        Handle S5F1
        """
        self.equipment.send_response(self.equipment.stream_function(5, 2)(
            ACKC5.ACCEPTED), packet.header.system)

        decode = self.equipment.secs_decode(packet)
        alarm_id = decode.ALID.get()
        alarm_cd = decode.ALCD.get()
        alarm_text = decode.ALTX.get()

        topic = f"equipments/status/alarm/{self.equipment.equipment_name}"
        message = f"alid: {alarm_id}, alcd: {alarm_cd},Alarm Text: {alarm_text}"

        self.equipment.mqtt_client.client.publish(topic, message)
