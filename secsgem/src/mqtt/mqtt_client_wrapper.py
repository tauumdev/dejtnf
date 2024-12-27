import paho.mqtt.client as mqtt
import logging
import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.equipment_manager import EquipmentManager

logger = logging.getLogger("app_logger")


class MQTTClientWrapper:
    def __init__(self, equipment_manager: 'EquipmentManager'):
        self.client = mqtt.Client(userdata=equipment_manager)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        logger.info("MQTT Client initialized")

    def on_connect(self, client: mqtt.Client, userdata, flags, rc):
        if rc == 0:  # Connection successful
            logger.info(f"Connected with result code {rc}")
            # Subscribe to control topics for equipment
            client.subscribe("equipment/mqttcontrol/#")
            logger.info("Subscribed to 'equipment/mqttcontrol/#' topic.")
            # Publish system status on connect
            client.publish("secsgem/status",
                           json.dumps({"status": "connected"}))
            logger.info("Published MQTT connection status: connected.")
        else:
            logger.error(f"Connection failed with result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            logger.warning("Unexpected disconnection from MQTT broker.")
        logger.info("Disconnected from MQTT broker. Equipment statuses:")

    def on_message(self, client: mqtt.Client, userdata: 'EquipmentManager', msg: mqtt.MQTTMessage):
        topic_parts = msg.topic.split("/")
        if len(topic_parts) == 3:
            equipment_name = topic_parts[2]
            command = msg.payload.decode("utf-8")
            logger.info("Received command %s for %s", command, equipment_name)
            # Control equipment based on received command
            if command == "online":
                userdata.online(equipment_name)
            elif command == "offline":
                userdata.offline(equipment_name)
            else:
                logger.warning("Unknown command %s for %s",
                               command, equipment_name)
                client.publish("equipment/mqttcontrol_response/" +
                               equipment_name, f"unknown_command {command}")

    def publish(self, topic, payload, qos=0, retain=False):
        self.client.publish(topic, payload, qos, retain)
        logger.info("Published to topic '%s' with payload '%s'",
                    topic, payload)

    def subscribe(self, topic, qos=0):
        self.client.subscribe(topic, qos)
        logger.info("Subscribed to topic '%s'", topic)

    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)
        logger.info("Unsubscribed from topic '%s'", topic)

    def connect(self, host, port=1883, keepalive=60):
        self.client.connect(host, port, keepalive)
        logger.info("Connected to MQTT broker at %s:%d", host, port)

    def disconnect(self):
        self.client.disconnect()
        # logger.info("Disconnected from MQTT broker")

    def loop_start(self):
        self.client.loop_start()
        logger.info("Started MQTT loop")

    def loop_stop(self):
        self.client.loop_stop()
        logger.info("Stopped MQTT loop")
