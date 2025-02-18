import logging
import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from config.app_config import MQTT_ENABLE, MQTT_SUBSCRIBE_TOPIC
# from mqtt.handler.handler_message import HandlerMessage
from src.mqtt.handler.handler_message import HandlerMessage
logger = logging.getLogger("app_logger")


class MqttClient:
    """
    Class for handling MQTT client
    """
    # load environment variables
    load_dotenv()

    mqtt_broker = os.getenv("MQTT_BROKER")
    mqtt_port = int(os.getenv("MQTT_PORT"))
    mqtt_username = os.getenv("MQTT_USERNAME")
    mqtt_password = os.getenv("MQTT_PASSWORD")

    def __init__(self):
        self.client = mqtt.Client()
        self.client.enable_logger(logger)
        self.client.username_pw_set(
            MqttClient.mqtt_username, MqttClient.mqtt_password)
        self.client.on_connect = self.on_connect
        self.client.on_message = HandlerMessage(self).on_message
        self.client.on_disconnect = self.on_disconnect

        if MQTT_ENABLE:
            self.client.connect(MqttClient.mqtt_broker, 1883, 60)
            self.client.loop_start()
            logger.info("MQTT client started")

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback function for when the client receives a CONNACK response from the server.
        """
        if rc == 0:
            logger.info("Connected to MQTT broker.")
            print("Connected to MQTT broker.")
            for topic in MQTT_SUBSCRIBE_TOPIC:
                self.client.subscribe(topic)
                logger.info("Subscribed to topic: %s", topic)
                print(f"Subscribed to topic: {topic}")
        else:
            logger.error("Connection failed with result code %s", rc)
            print(f"Connection failed with result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """
        Callback function for when the client disconnects from the server.
        """
        if rc != 0:
            logger.warning("Unexpected disconnection. Reconnecting...")
            print("Unexpected disconnection. Reconnecting...")
            self.client.reconnect()
        else:
            logger.info("Disconnected from MQTT broker")
            print("Disconnected from MQTT broker")
