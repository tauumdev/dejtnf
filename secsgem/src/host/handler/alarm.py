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
        # self.pending_alarms = set()

    def alarms_list(self):
        """
        Get alarms list
        """
        vid_al = {"FCL": 24, "FCLX": 2}
        alids = self.gemhost.secs_control.select_equipment_status_request(
            vid_al.get(self.gemhost.equipment_model))
        # print(alids)
        return alids

    def receive_alarm(self, handler: secsgem.secs.SecsHandler, message: secsgem.common.Message):
        """
        Receive alarm
        """
        handler.send_response(self.gemhost.stream_function(
            5, 2)(ACKC5.ACCEPTED), message.header.system)
        decode = self.gemhost.settings.streams_functions.decode(message)

        alid = decode.ALID.get()
        alcd = decode.ALCD.get()
        altx = decode.ALTX.get().strip()

        topic = f"equipments/status/alarm/{self.gemhost.equipment_name}/{alid}"
        if alcd == 0:
            self.gemhost.mqtt_client.client.publish(
                topic, None, qos=2, retain=True)
            # self.pending_alarms.remove(alid)
        else:
            self.gemhost.mqtt_client.client.publish(
                topic, altx, qos=2, retain=True)
            # self.pending_alarms.add(alid)

    # def clear_pending_alarms(self):
    #     """
    #     Clear pending alarms
    #     """
    #     logger.info("Clearing pending alarms")
    #     for alid in self.pending_alarms:
    #         topic = f"equipments/status/alarm/{self.gemhost.equipment_name}/{alid}"
    #         self.gemhost.mqtt_client.client.publish(topic, None, retain=True)
    #     self.pending_alarms.clear()
