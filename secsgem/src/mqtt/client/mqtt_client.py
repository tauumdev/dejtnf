import logging
import sys
import os
import paho.mqtt.client as mqtt

from dotenv import load_dotenv

from src.mqtt.handler.handler_message import HandlerMessage
from src.utils.config.app_config import ENABLE_MQTT, MQTT_SUBSCRIBE_TOPIC

logger = logging.getLogger("app_logger")

load_dotenv()

mqtt_broker = os.getenv("MQTT_BROKER")
mqtt_port = int(os.getenv("MQTT_PORT"))
mqtt_username = os.getenv("MQTT_USERNAME")
mqtt_password = os.getenv("MQTT_PASSWORD")


class MqttClient:
    """
    MQTT Client class
    """

    def __init__(self):
        self.client = mqtt.Client()
        # self.client.enable_logger(logger)
        self.client.on_connect = self.on_connect
        self.client.on_message = HandlerMessage(self).on_message
        self.client.on_disconnect = self.on_disconnect

        if ENABLE_MQTT:
            logger.info("MQTT enabled. Connecting to broker...")
            try:
                self.client.username_pw_set(
                    username=mqtt_username, password=mqtt_password)
                self.client.connect(mqtt_broker, mqtt_port, 60)
                self.client.loop_start()
                logger.info("MQTT client started.")
            except Exception as e:
                logger.error(f"Error connecting to MQTT broker: {e}")
        else:
            logger.info("MQTT disabled. Skipping connection to broker.")

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback function for when the client receives a CONNACK response from the server.
        """
        if rc == 0:
            logger.info("Connected to MQTT broker.")
            for topic in MQTT_SUBSCRIBE_TOPIC:
                self.client.subscribe(topic)
                logger.info(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Connection failed with result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """
        Callback function for when the client disconnects from the server.
        """
        if rc != 0:
            logger.error("Unexpected disconnection. Reconnecting...")
            self.client.reconnect()
        else:
            logger.info("Disconnected from MQTT broker")
