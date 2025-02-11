import logging
import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from src.utils.config.app_config import MQTT_SUBSCRIBE_TOPIC, MQTT_ENABLE

from src.gemhost.equipment import Equipment

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
        self.client.on_message = self._HandlerMessage(self).on_message
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
            # print("Connected to MQTT broker.")
            for topic in MQTT_SUBSCRIBE_TOPIC:
                self.client.subscribe(topic)
                logger.info("Subscribed to topic: %s", topic)
                # print(f"Subscribed to topic: {topic}")
        else:
            logger.error("Connection failed with result code %s", rc)
            # print(f"Connection failed with result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """
        Callback function for when the client disconnects from the server.
        """
        if rc != 0:
            # print("Unexpected disconnection. Reconnecting...")
            logger.warning("Unexpected disconnection. Reconnecting...")
            self.client.reconnect()
        else:
            logger.info("Disconnected from MQTT broker")
            # print("Disconnected from MQTT broker")

    class _HandlerMessage:
        """
        Class for handling MQTT messages
        """

        def __init__(self, mqtt_client_instant: "MqttClient"):
            self.mqtt_client = mqtt_client_instant

        def on_message(self, client, userdata, msg: mqtt.MQTTMessage):
            """
            Callback function for when a PUBLISH message is received from the server.
            """
            logger.info("Received message: %s", msg.payload)

            equipments = userdata.get("equipments", [])
            if isinstance(equipments, list):
                if len(equipments) == 0:
                    logger.warning("Equipments not found in userdata")
                for equipment in equipments:
                    if isinstance(equipment, Equipment):
                        print("Userdata is a list of Equipment: ",
                              equipment.equipment_name)
                        print("Handle message with equipment here")
                    else:
                        logger.warning("Userdata is not a list of Equipment")
            else:
                logger.warning("Userdata is not a list")
