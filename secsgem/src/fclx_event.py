class FCLXEvent:
    def __init__(self):
        # Initialize any necessary attributes here
        pass

    def handle_ceid(self, ceid, message):
        # Add your logic to handle the CEID here
        print(f"Handling CEID: {ceid}")

        try:
            decode = self.settings.streams_functions.decode(message)
        except Exception as e:
            print(f"Error decoding message: {e}")
            return

        ceid_code = {8: "offline", 9: "online/local", 10: "online/remote"}
        _state = ceid_code.get(ceid, f"Unknown code: {ceid}")

        try:
            self.mqtt_client.publish(f"hosts/{self.machine_name}/controlstate", _state)
        except Exception as e:
            print(f"Error publishing to MQTT: {e}")
