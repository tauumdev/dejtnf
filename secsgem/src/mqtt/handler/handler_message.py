import logging
import paho.mqtt.client as mqtt

logger = logging.getLogger("app_logger")


class HandlerMessage:
    """
    Class for handling MQTT messages
    """

    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def on_message(self, client, userdata, message: mqtt.MQTTMessage):
        """
        Callback function for when a PUBLISH message is received from the server.
        """
        payload = message.payload.decode("utf-8")
        topic = message.topic
        print(f"Received message: {payload} from topic: {topic}")
        logger.info("Received message: %s from topic: %s", payload, topic)
        # self.mqtt_client.client.publish("test", "test")
        # print("Published message: test to topic: test")
        # logger.info("Published message: test to topic: test")
