import logging

from typing import TYPE_CHECKING

import secsgem.common
import secsgem.secs
from secsgem.secs.data_items import ACKC5

if TYPE_CHECKING:
    from host.gemhost import SecsGemHost
    from mqtt.mqtt_client import MqttClient

logger = logging.getLogger("app_logger")


class HandlerAlarm:
    """
    Class for handling receive alarm
    """

    def __init__(self, gemhost: "SecsGemHost"):
        self.gemhost = gemhost

    def receive_alarm(self, handler: secsgem.secs.SecsHandler, message: secsgem.common.Message):
        """
        Receive alarm
        """
        handler.send_response(self.gemhost.stream_function(
            5, 2)(ACKC5.ACCEPTED), message.header.system)
        decode = self.gemhost.settings.streams_functions.decode(message)

        self.gemhost.mqtt_client.client.publish(
            f"equipments/status/alarm/{self.gemhost.equipment_name}", f"ALID: {decode.ALID.get()} ALCD: {decode.ALCD.get()} ALTX: {decode.ALTX.get()}")
