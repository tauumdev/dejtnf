class MQTTHandler:
    def __init__(self, broker, port, topic, on_message_callback):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.on_message_callback = on_message_callback
        self.client = None

    def connect(self):
        import paho.mqtt.client as mqtt

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        self.on_message_callback(msg.topic, msg.payload)

    def publish(self, topic, payload):
        if self.client:
            self.client.publish(topic, payload)

    def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()