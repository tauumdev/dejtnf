# secsgem/src/host/gem_host.py
import logging
import secsgem.common
import paho.mqtt.client as mqtt
import secsgem.gem
import secsgem.hsms
import secsgem.secs
# import secsgem.secs.functions.streams_functions

from utils.secsgem_logging import CommunicationLogFileHandler

# Initialize logger for the application
logger = logging.getLogger("app_logger")


class DejtnfHost(secsgem.gem.GemHostHandler):
    # Initialize the host with settings, equipment name, and model
    def __init__(self, settings: secsgem.common.Settings, equipment_name: str, equipment_model: str, mqtt_client: mqtt.Client):
        super().__init__(settings)
        self.MDLN = "dejtnf"  # Model name
        self.SOFTREV = "1.0.0"  # Software revision
        self.equipment_name = equipment_name
        self.equipment_model = equipment_model
        self.mqtt_client = mqtt_client
        self._enabled = False  # Status of the equipment

        # Register SECS message handlers
        self.register_stream_function(1, 14, self._on_s01f14)

        # Attach an event handler for disconnection
        self._protocol.events.disconnected += self.on_connection_closed

    # Check if the equipment is enabled
    def is_enabled(self):
        return self._enabled

    # Enable the equipment
    def enable(self):
        logger.info(self.equipment_name)
        self.mqtt_client.publish(
            f"equipment/enable/{self.equipment_name}", "enabled")
        self._enabled = True
        return super().enable()

    # Disable the equipment
    def disable(self):
        logger.info(self.equipment_name)
        self.mqtt_client.publish(
            f"equipment/enable/{self.equipment_name}", "disabled")
        self._enabled = False
        return super().disable()

    # Wait for communication to be established
    def waitfor_communicating(self, timeout=None):
        super().waitfor_communicating(timeout)

        current_state = self._communication_state.current.name
        logger.info("%s %s", current_state, self.equipment_name)

        self.mqtt_client.publish(
            f"equipment/communication/{self.equipment_name}", current_state)

    # Handle communicating state changes
    def _on_communicating(self, _):
        super()._on_communicating(_)
        current_state = self._communication_state.current.name
        logger.info("%s %s", current_state, self.equipment_name)

        self.mqtt_client.publish(
            f"equipment/communication/{self.equipment_name}", current_state)

    # Handle state transitions to communicating
    def _on_state_communicating(self, _):
        super()._on_state_communicating(_)
        logger.info(self.equipment_name)
        current_state = self._communication_state.current.name
        logger.info("%s %s", current_state, self.equipment_name)

        self.mqtt_client.publish(
            f"equipment/communication/{self.equipment_name}", current_state)
    # Handle communication closure events

    def on_connection_closed(self, _):
        super().on_connection_closed(_)
        current_state = "NOT_COMMUNICATING"
        logger.info("%s %s", current_state, self.equipment_name)

        self.mqtt_client.publish(
            f"equipment/communication/{self.equipment_name}", current_state)

    def go_online(self):
        logger.info(self.equipment_name)
        result = super().go_online()
        return result

    def go_offline(self):
        logger.info(self.equipment_name)
        result = super().go_offline()
        return result

    # # Process SECS message S1F13 (establish communication request)
    # def _on_s01f13(self, handler, message):
    #     logger.info(self.equipment_name)
    #     return super()._on_s01f13(handler, message)

    # Process SECS message S1F14 (establish communication response)
    def _on_s01f14(self, handler, message):
        logger.info(self.equipment_name)

    # Process SECS message S5F1 (alarm report)
    def _on_s05f01(self, handler, message):
        # logger.info(self.equipment_name)
        self.send_response(
            self.stream_function(5, 2)(
                secsgem.secs.data_items.ACKC5.ACCEPTED),
            message.header.system,
        )
        # Decode and log the received message
        decode = self.settings.streams_functions.decode(message)
        self.mqtt_client.publish(
            f"equipment/S5F1/{self.equipment_name}", str(decode))

    # Process SECS message S6F11 (event report)
    def _on_s06f11(self, handler, message):
        # logger.info(self.equipment_name)
        # Send acknowledgment response
        self.send_response(
            self.stream_function(6, 12)(
                secsgem.secs.data_items.ACKC6.ACCEPTED),
            message.header.system,
        )
        # Decode and log the received CEID
        decode = self.settings.streams_functions.decode(message)
        self.mqtt_client.publish(
            f"equipment/S6F11/{self.equipment_name}", str(decode))

        # ceid = decode.CEID.get()
        # logger.info(f"CEID: {ceid}")


# Configure communication log file handler
commLogFileHandler = CommunicationLogFileHandler("logs", "h")
commLogFileHandler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
logging.getLogger("communication").addHandler(commLogFileHandler)
logging.getLogger("communication").propagate = False

# Configure basic logging format and level
logging.basicConfig(
    format='%(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.INFO)
