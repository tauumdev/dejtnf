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
        # self.client.on_message = HandlerMessage(self).on_message
        self.handler_message = HandlerMessage(self)
        self.client.on_message = self.handler_message.on_message
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

    def publish(self, topic: str, payload: str, qos: int = 0, retain: bool = False):
        """
        Publish a message to a specific MQTT topic.
        Args:
            topic (str): The topic to publish to.
            payload (str): The message payload.
            qos (int): Quality of Service level (0, 1, or 2).
            retain (bool): Whether to retain the message on the broker.
        """
        try:
            result = self.client.publish(
                topic, payload, qos=qos, retain=retain)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info("Published to %s: %s", topic, payload)
                print(f"Published to {topic}: {payload}")
            else:
                logger.error(
                    "Failed to publish to %s. Error code: %s", topic, result.rc)
                print(f"Failed to publish to {topic}. Error code: {result.rc}")
        except Exception as e:
            logger.error("Error publishing to %s: %s", topic, str(e))
            print(f"Error publishing to {topic}: {str(e)}")

    def subscribe(self, topic: str, qos: int = 0):
        """
        Subscribe to a specific MQTT topic.
        Args:
            topic (str): The topic to subscribe to.
            qos (int): Quality of Service level (0, 1, or 2).
        """
        try:
            result, mid = self.client.subscribe(topic, qos=qos)
            if result == mqtt.MQTT_ERR_SUCCESS:
                logger.info("Subscribed to %s with QoS %s", topic, qos)
                print(f"Subscribed to {topic} with QoS {qos}")
            else:
                logger.error(
                    "Failed to subscribe to %s. Error code: %s", topic, result)
                print(f"Failed to subscribe to {topic}. Error code: {result}")
        except Exception as e:
            logger.error("Error subscribing to %s: %s", topic, str(e))
            print(f"Error subscribing to {topic}: {str(e)}")
