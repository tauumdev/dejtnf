
class mqtt_message:
    def __init__(self, topic, message):
        self.topic = topic
        self.message = message

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code: {rc}")
        self.subscribe("equipment/control")

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        print(f"Message received: {message}")
        self.handle_command(message)
