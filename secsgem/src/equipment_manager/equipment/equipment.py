import logging
import threading
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs

from src.equipment_manager.equipment.core.function_control import FunctionControl
from src.equipment_manager.equipment.handler.events.handler_events import EventsCallbacks
from src.equipment_manager.equipment.handler.alarm.handler_alarm import AlarmCallbacks
from src.equipment_manager.equipment.callbacks.stream_function import RegisterCallbacks
from src.equipment_manager.equipment.custom_stream_function.stream_function import SecsS02F49, SecsS02F50

from src.utils.logger.gem_logger import CommunicationLogFileHandler
from src.mqtt.client.mqtt_client import MqttClient

from src.utils.config.secsgem_subscribe import SUBSCRIBE_LOT_CONTROL_FCL, SUBSCRIBE_LOT_CONTROL_FCLX

logger = logging.getLogger("app_logger")

commLogFileHandler = CommunicationLogFileHandler("logs/gem")
commLogFileHandler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
logging.getLogger("hsms_communication").addHandler(commLogFileHandler)
logging.getLogger("hsms_communication").propagate = False

# Configure basic logging format and level
logging.basicConfig(
    format='%(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.INFO)


class Equipment(secsgem.gem.GemHostHandler):

    def __init__(self, name: str, equipment_model: str, address, port: int,  session_id: int, active: bool, is_enable: bool, mqtt_client: MqttClient, custom_connection_handler=None):

        super().__init__(address, port, active, session_id, name, custom_connection_handler)
        self.mqtt_client = mqtt_client
        self.equipment_name = name
        self.equipment_model = equipment_model
        self.MDLN = "dejtnf"
        self.SOFTREV = "1.0.1"
        self.is_enabled = is_enable
        # self.lot_active = None

        self.secsStreamsFunctions[2].update({49: SecsS02F49, 50: SecsS02F50})

        self.register_callbacks = RegisterCallbacks(self)
        self.register_stream_function(1, 14, self.register_callbacks.s01f14)
        self.register_stream_function(9, 1, self.register_callbacks.s09f1)
        self.register_stream_function(9, 3, self.register_callbacks.s09f3)
        self.register_stream_function(9, 5, self.register_callbacks.s09f5)
        self.register_stream_function(9, 7, self.register_callbacks.s09f7)
        self.register_stream_function(9, 9, self.register_callbacks.s09f9)
        self.register_stream_function(9, 11, self.register_callbacks.s09f11)

        self.handle_alarm = AlarmCallbacks(self)
        self.register_stream_function(5, 1, self.handle_alarm._on_s05f01)

        self.handle_event = EventsCallbacks(self)
        self.register_stream_function(6, 11, self.handle_event._on_s06f11)

        self.fc_control = FunctionControl(self)

    def delayed_task(self):
        """
        Delayed task for subscribe lot
        """
        wait_seconds = 0.05
        logger.info("Task started, waiting for %s seconds...", wait_seconds)
        threading.Event().wait(wait_seconds)  # Non-blocking wait
        logger.info("%s seconds have passed!\n", wait_seconds)

        # subscribe lot control
        self.fc_control.subscribe_lot_control()

    def _on_state_communicating(self, _):
        super()._on_state_communicating(_)

        current_state = self.communicationState.current
        logger.info("%s On communication state: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)

        # Start the thread
        thread = threading.Thread(target=self.delayed_task)
        thread.start()

    def on_connection_closed(self, connection):
        super().on_connection_closed(connection)

        current_state = self.communicationState.current
        logger.info("%s On connection close: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)

    def _on_state_disconnect(self):
        super()._on_state_disconnect()

        current_state = "NOT_COMMUNICATING"
        logger.info("%s On state disconnect: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)
