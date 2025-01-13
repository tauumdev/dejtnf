import logging
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs

from ..mqttclient.mqtt_client_wrapper import MqttClient
from ..core.secs_handler_fcl import HandlerFcl
from ..core.secs_handler_fclx import HandlerFclx

logger = logging.getLogger("app_logger")


class Equipment(secsgem.gem.GemHostHandler):
    """
    Represents a single equipment instance.
    """

    def __init__(self, settings: secsgem.common.Settings, equipment_name: str, equipment_model: str, is_enable: bool, mqtt_client: MqttClient):
        """
        Initialize the equipment instance.

        Args:
            settings (secsgem.common.Settings): The settings for the equipment.
            equipment_name (str): The name of the equipment.
            equipment_model (str): The model of the equipment.
            is_enable (bool): Whether the equipment is enabled.
            mqtt_client (MqttClient): The MQTT client instance.
        """
        super().__init__(settings)
        self.equipment_name = equipment_name
        self.equipment_model = equipment_model
        self.is_enabled = is_enable
        self.MDLN = "dejtnf"
        self.SOFTREV = "1.0.1"

        self.register_stream_function(1, 14, self.s01f14)
        self.register_stream_function(9, 1, self.s09f1)
        self.register_stream_function(9, 3, self.s09f3)
        self.register_stream_function(9, 5, self.s09f5)
        self.register_stream_function(9, 7, self.s09f7)
        self.register_stream_function(9, 9, self.s09f9)
        self.register_stream_function(9, 11, self.s09f11)

        self._protocol.events.disconnected += self.on_connection_closed

        self.mqtt_client = mqtt_client

    def _on_communicating(self, _):
        """
        Logs the communication state of the equipment.
        """
        current_state = self._communication_state.current.name
        logger.info("%s Communication state: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)
        return super()._on_communicating(_)

    def _on_state_communicating(self, _):
        """
        Logs the communication state of the equipment.
        """
        current_state = self._communication_state.current.name
        logger.info("%s Communication state: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)
        self.mqtt_client.client.publish(
            f"equipments/status/control_state/{self.equipment_name}", 'selected', qos=1, retain=True)
        return super()._on_state_communicating(_)

    def on_connection_closed(self, _):
        """
        Logs the communication state of the equipment.
        """
        # current_state = self._communication_state.current.name
        current_state = "NOT_COMMUNICATING"
        logger.info("%s Communication state: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)
        self.mqtt_client.client.publish(
            f"equipments/status/control_state/{self.equipment_name}", 'closed', qos=1, retain=True)
        return super().on_connection_closed(_)

    def s01f14(self, handle, packet):
        self.mqtt_client.client.publish(
            f"equipments/status/control_state/{self.equipment_name}", 'online')

    def s09f1(self, handle, packet):
        logger.warning("s09f1:Unrecognized Device ID (UDN): %s",
                       self.equipment_name)

    def s09f3(self, handle, packet):
        logger.warning("s09f3:Unrecognized Stream Function (SFCD): %s",
                       self.equipment_name)

    def s09f5(self, handle, packet):
        logger.warning("s09f5:Unrecognized Function Type (UFN): %s",
                       self.equipment_name)

    def s09f7(self, handle, packet):
        logger.warning("s09f7:Illegal Data (IDN): %s",
                       self.equipment_name)

    def s09f9(self, handle, packet):
        logger.warning("s09f9:Transaction Timer Timeout (TTN): %s",
                       self.equipment_name)

    def s09f11(self, handle, packet):
        logger.warning("s09f11:Data Too Long (DLN): %s",
                       self.equipment_name)

    def _on_alarm_received(self, handler, alarm_id, alarm_code, alarm_text):
        super()._on_alarm_received(handler, alarm_id, alarm_code, alarm_text)
        logger.info("Alarm received: %s", alarm_text)
        msg = {"alcd": alarm_code.get(), "alid": alarm_id.get(),
               "altx": alarm_text.get().strip()}

        self.mqtt_client.client.publish(
            f"equipments/status/alarm/{self.equipment_name}", str(msg))

        rsp = self.send_and_waitfor_response(self.stream_function(2, 13)([81]))

        s02f14 = self.settings.streams_functions.decode(rsp)
        logger.info("S2F14 response: %s", s02f14)

    def _on_s06f11(self, handler, message: secsgem.common.Message):
        self.send_response(self.stream_function(6, 12)(
            secsgem.secs.data_items.ACKC6.ACCEPTED), message.header.system)

        s6f11 = self.settings.streams_functions.decode(message)
        self.mqtt_client.client.publish(
            f"equipments/status/s6f11/{self.equipment_name}", str(s6f11))

        # if self.equipment_model == "FCL":
        #     HandlerFcl().handle_s6f11(handler, message)
        # elif self.equipment_model == "FCLX":
        #     HandlerFclx().handle_s6f11(handler, message)

        if s6f11.CEID.get() == 20:
            # rsp = self.send_remote_command(
            #     rcmd="LOT_ACCEPT", params=[["LotID", "123456"]])
            # logger.info("Remote command response: %s", rsp)

            print("CEID 20")
            rsp = handler.settings.streams_functions.decode(handler.send_and_waitfor_response(
                handler.stream_function(2, 13)([81])))

            print(rsp)
