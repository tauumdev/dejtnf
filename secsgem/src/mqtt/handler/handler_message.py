import logging
import paho.mqtt.client as mqtt

logger = logging.getLogger("app_logger")


class HandlerMessage:
    """
    Class to handle MQTT messages
    """

    def __init__(self, mqtt_client: mqtt.Client):
        self.client = mqtt_client

    def on_message(self, client, userdata, message: mqtt.MQTTMessage):
        """
        Callback function for when a PUBLISH message is received from the server.
        """
        logger.info(f"Received message on topic {
                    message.topic}: {message.payload}")
        # Add message handling logic here
        pass
