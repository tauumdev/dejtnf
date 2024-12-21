# dejtnf-v1 gemhosthandler control equipment by cli and mqtt
# secsgem library https://github.com/bparzella/secsgem
# mqtt library https://github.com/eclipse/paho.mqtt.python

import json
import logging
import os
import cmd
import paho.mqtt.client as mqtt

import secsgem.common
import secsgem.gem
import secsgem.hsms


class CommunicationLogFileHandler(logging.Handler):
    """Handler for logging communication to a file.

    Args:
        path (str): The directory path where log files will be stored.
        prefix (str): The prefix for the log file names.
    """

    def __init__(self, path, prefix=""):
        logging.Handler.__init__(self)

        self.path = path
        self.prefix = prefix

    def emit(self, record):
        filename = os.path.join(self.path, "{}com_{}.log".format(
            self.prefix, record.remoteName))
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(self.format(record) + "\n")


class SampleEquipment(secsgem.gem.GemHostHandler):
    """
    SampleEquipment is a subclass of secsgem.gem.GemHostHandler that initializes
    a GEM host handler with specific settings.

    Attributes:
        equipment_name (str): Name of the equipment.
        SOFTREV (str): Software revision of the GEM host.
        enabled (bool): Status of the GEM host.

    Args:
        equipment_settings (secsgem.common.Settings): The settings for the GEM host.
        equipment_name (str): Name of the equipment.
    """

    def __init__(self, equipment_settings: secsgem.common.Settings, equipment_name: str):
        super().__init__(equipment_settings)

        self.equipment_name = equipment_name
        self.SOFTREV = "1.0.0"
        self.enabled = False

        # Hardcoded MQTT broker and port
        self.mqtt_broker = "localhost"
        self.mqtt_port = 1883

        # Initialize MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, 60)
        self.enable_mqtt()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(f"equipment/{self.equipment_name}/connection")

    def on_message(self, client, userdata, msg):
        print(f"Message received: {msg.topic} {msg.payload}")
        if msg.topic == f"equipment/{self.equipment_name}/connection":
            if msg.payload.decode() == "enable":
                self.enable()
            elif msg.payload.decode() == "disable":
                self.disable()

    def enable(self):
        if not self.enabled:
            super().enable()
            self.enabled = True
            self.mqtt_client.publish(
                f"equipment/{self.equipment_name}/status", "enabled")
            print(f"Equipment {self.equipment_name} enabled.")
        else:
            print(f"Equipment {self.equipment_name} is already enabled.")
            self.mqtt_client.publish(
                f"equipment/{self.equipment_name}/status", "already enabled")

    def disable(self):
        if self.enabled:
            super().disable()
            self.enabled = False
            self.mqtt_client.publish(
                f"equipment/{self.equipment_name}/status", "disabled")
            print(f"Equipment {self.equipment_name} disabled.")
        else:
            print(f"Equipment {self.equipment_name} is already disabled.")
            self.mqtt_client.publish(
                f"equipment/{self.equipment_name}/status", "already disabled")

    def enable_mqtt(self):
        self.mqtt_client.loop_start()
        print("MQTT enabled.")

    def disable_mqtt(self):
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        print("MQTT disabled.")


commLogFileHandler = CommunicationLogFileHandler("log", "h")
commLogFileHandler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
logging.getLogger("communication").addHandler(commLogFileHandler)
logging.getLogger("communication").propagate = False

logging.basicConfig(
    format='%(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.DEBUG)

# Load configuration from config.json
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

equipments = {}

# Initialize equipments based on configuration
for equipment_config in config["equipment"]:
    settings = secsgem.hsms.HsmsSettings(
        address=equipment_config["address"],
        port=equipment_config["port"],
        session_id=equipment_config["session_id"],
        connect_mode=secsgem.hsms.HsmsConnectMode[equipment_config["connect_mode"]],
        device_type=secsgem.common.DeviceType[equipment_config["device_type"]]
    )
    equipment = SampleEquipment(settings, equipment_config["equipment_name"])
    equipments[equipment_config["equipment_name"]] = (
        equipment, equipment_config["enable"])

# Enable or disable equipments based on configuration
for equipment, enable in equipments.values():
    if enable:
        equipment.enable()


class HostCmd(cmd.Cmd):
    """Command-line interface for managing equipments."""

    prompt = "(hostcmd) "

    def do_enable(self, arg):
        """Enable an equipment by name. Usage: enable <equipment_name>"""
        equipment_name = arg.strip()
        if equipment_name in equipments:
            equipment, _ = equipments[equipment_name]
            equipment.enable()
            print(f"Equipment {equipment_name} enabled.")
        else:
            print("Invalid equipment name.")

    def do_disable(self, arg):
        """Disable an equipment by name. Usage: disable <equipment_name>"""
        equipment_name = arg.strip()
        if equipment_name in equipments:
            equipment, _ = equipments[equipment_name]
            equipment.disable()
            print(f"Equipment {equipment_name} disabled.")
        else:
            print("Invalid equipment name.")

    def do_exit(self, arg):
        """Exit the program."""
        print("Exiting...")
        return True

    def do_list(self, arg):
        """List all equipments and their status."""
        for equipment_name, (equipment, enable) in equipments.items():
            status = "enabled" if equipment.enabled else "disabled"
            print(f"Equipment {equipment_name}: {status}")


if __name__ == "__main__":
    HostCmd().cmdloop()

    # Disable all equipments before exiting
    for equipment, _ in equipments.values():
        if equipment.enabled:
            equipment.disable()
        equipment.mqtt_client.loop_stop()
        equipment.mqtt_client.disconnect()
