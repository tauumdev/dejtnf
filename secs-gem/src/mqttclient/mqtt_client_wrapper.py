import json
import logging
import paho.mqtt.client as mqtt

from src.core.mqtt_handler_message import MqttMessageHandler
from src.utils.config_loader import load_config
from src.config.config import EQ_CONFIG_PATH, MQTT_CONFIG_PATH, ENABLE_MQTT

logger = logging.getLogger("config_loader")


class MqttClient:
    """
    Manages the MQTT client connection and message handling.
    """

    def __init__(self, config_path):
        """
        Initialize the MQTT client with the given configuration.

        Args:
            config_path (str): Path to the MQTT configuration file.
        """
        self.client = mqtt.Client()
        self.client.enable_logger(logger)
        self.client.on_connect = self.on_connect
        self.client.on_message = MqttMessageHandler().on_message
        self.client.on_disconnect = self.on_disconnect

        if ENABLE_MQTT:
            self.load_config(config_path)

    def load_config(self, config_path):
        """
        Load the MQTT configuration and connect to the broker.

        Args:
            config_path (str): Path to the MQTT configuration file.
        """
        try:
            logger.info("Initializing MQTT client...")
            config = load_config(
                config_path, ["broker", "port", "username", "password", "keepalive"])
            self.client.username_pw_set(config["username"], config["password"])
            self.client.connect(
                config["broker"], config["port"], keepalive=config.get("keepalive", 60))
            self.client.loop_start()
            logger.info("MQTT loop started.")
        except Exception as e:
            logger.error("Failed to initialize MQTT client: %s", e)
            raise

    def close(self):
        """
        Disconnect the MQTT client and stop the loop.
        """
        try:
            self.client.disconnect()
            self.client.loop_stop()
            logger.info("MQTT client disconnected and loop stopped.")
        except Exception as e:
            logger.error("Error during MQTT client shutdown: %s", e)

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback when the client connects to the broker.

        Args:
            client (mqtt.Client): The MQTT client instance.
            userdata: The user data.
            flags: Response flags sent by the broker.
            rc (int): The connection result.
        """
        if rc == 0:
            self.client.subscribe("equipment/control/#")
            self.client.subscribe("equipment/config/#")
            logger.info(
                "MQTT connection established. Subscribed to %s",  "equipment/control/#")
        else:
            logger.error(
                "Failed to connect to MQTT broker. Return code: %d", rc)

    def on_disconnect(self, client, userdata, rc):
        """
        Callback when the client disconnects from the broker.

        Args:
            client (mqtt.Client): The MQTT client instance.
            userdata: The user data.
            rc (int): The disconnection result.
        """
        if rc == 0:
            logger.info("MQTT connection closed gracefully.")
        else:
            logger.error("MQTT connection closed unexpectedly.")
