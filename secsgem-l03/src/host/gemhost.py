
import datetime
import logging
import os
import threading

import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.secs.data_items import ACKC6, ACKC5, ACKC7

from src.host.handler.alarm import HandlerAlarm
from src.host.handler.event import HandlerEvent
from src.host.handler.control import SecsControl
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mqtt.mqtt_client import MqttClient

logger = logging.getLogger("app_logger")


class CommunicationLogFileHandler(logging.Handler):
    """
    Custom logging handler that writes logs to a file based on the IP address of the equipment.
    """

    def __init__(self, path):
        logging.Handler.__init__(self)

        self.path = path

    def emit(self, record):
        ip_without_dots = record.address.replace(".", "")
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = os.path.join(
            self.path, ip_without_dots, "{}_{}.log".format(record.address, date))
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(self.format(record) + "\n")


commLogFileHandler = CommunicationLogFileHandler("logs/gem")
commLogFileHandler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
logging.getLogger("communication").addHandler(commLogFileHandler)
logging.getLogger("communication").propagate = False

logging.basicConfig(
    format='%(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.INFO)


class SecsGemHost(secsgem.gem.GemHostHandler):
    """
    SECS/GEM equipment class
    """

    def __init__(self, equipment_name: str, equipment_model: str, enable: bool, mqtt_client: 'MqttClient', settings: secsgem.common.Settings):
        super().__init__(settings)
        self.mqtt_client = mqtt_client
        self.equipment_name = equipment_name
        self.equipment_model = equipment_model
        self.control_state = None
        self.process_state = None
        self.process_program = None
        self.active_lot = None
        self.is_enable = enable
        self.MDLN = "DEJTNF-HOST"
        self.SOFTREV = "1.0.0"

        self.register_stream_function(1, 14, self.on_s01f14)
        self.register_stream_function(9, 1, self.s09f1)
        self.register_stream_function(9, 3, self.s09f3)
        self.register_stream_function(9, 5, self.s09f5)
        self.register_stream_function(9, 7, self.s09f7)
        self.register_stream_function(9, 9, self.s09f9)
        self.register_stream_function(9, 11, self.s09f11)

        self.register_stream_function(5, 1, HandlerAlarm(self).receive_alarm)
        self.register_stream_function(6, 11, HandlerEvent(self).receive_event)
        self.secs_control = SecsControl(self)
        self.register_stream_function(7, 3, self.secs_control.pp_recive)

        self._protocol.events.disconnected += self.on_connection_closed

        if self.is_enable:
            self.enable()

    @property
    def is_communicating(self):
        """Check if equipment is communicating"""
        return self.communication_state.current.name == "COMMUNICATING"

    @property
    def is_online(self):
        """Check if equipment is online"""
        if self.control_state in ["On-Line", "On-Line/Local", "On-Line/Remote"]:
            return True
        return False

    def _on_message_received(self, data):
        """Handle received message from equipment passes to MQTT"""
        message = data["message"]
        self.mqtt_client.client.publish(
            f"equipments/status/secs_message/{self.equipment_name}", str(self.settings.streams_functions.decode(message)))
        return super()._on_message_received(data)

    def _on_state_wait_cra(self, _):
        super()._on_state_wait_cra(_)
        print("On wait cra - Communication state: ",
              self.communication_state.current.name)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", self.communication_state.current.name)

    def _on_state_communicating(self, _):
        super()._on_state_communicating(_)
        state = self.communication_state.current.name
        print("On communicating - Communication state: ",
              state)

        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", state)
        if state == "COMMUNICATING":
            # initial subscribe lot control
            threading.Timer(
                0.1, self.secs_control.initial_equipment).start()

    def on_connection_closed(self, _):
        super().on_connection_closed(_)
        print("On closed - Communication state: ",
              self.communication_state.current.name)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", self.communication_state.current.name)

    def on_s01f14(self, handle, message):
        logger.info("received s01f14: %s", self.equipment_name)

    def s09f1(self, handle, message):
        """Unrecognized Device ID"""
        logger.warning("s09f1:Unrecognized Device ID (UDN): %s",
                       self.equipment_name)
        print("s09f1:Unrecognized Device ID (UDN): ",
              self.equipment_name)

    def s09f3(self, handle, message):
        """Unrecognized Stream Function"""
        logger.warning("s09f3:Unrecognized Stream Function (SFCD): %s",
                       self.equipment_name)
        print("s09f3:Unrecognized Stream Function (SFCD): ",
              self.equipment_name)

    def s09f5(self, handle, message):
        """Unrecognized Function Type"""
        logger.warning("s09f5:Unrecognized Function Type (UFN): %s",
                       self.equipment_name)
        print("s09f5:Unrecognized Function Type (UFN): ",
              self.equipment_name)

    def s09f7(self, handle, message):
        """Illegal Data (IDN)"""
        logger.warning("s09f7:Illegal Data (IDN): %s",
                       self.equipment_name)
        print("s09f7:Illegal Data (IDN): ",
              self.equipment_name)

    def s09f9(self, handle, message):
        """Transaction Timer Timeout (TTN)"""
        logger.warning("s09f9:Transaction Timer Timeout (TTN): %s",
                       self.equipment_name)
        print("s09f9:Transaction Timer Timeout (TTN): ",
              self.equipment_name)

    def s09f11(self, handle, message):
        """Data Too Long (DLN)"""
        logger.warning("s09f11:Data Too Long (DLN): %s",
                       self.equipment_name)
        print("s09f11:Data Too Long (DLN): ",
              self.equipment_name)
