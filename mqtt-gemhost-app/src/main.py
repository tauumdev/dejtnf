import json
import logging
import os
import cmd
import paho.mqtt.client as mqtt

import secsgem.common
import secsgem.gem
import secsgem.hsms
from mqtt_handler import MQTTHandler


class CommunicationLogFileHandler(logging.Handler):
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
    def __init__(self, equipment_settings: secsgem.common.Settings):
        super().__init__(equipment_settings)
        self.MDLN = "gemhost"
        self.SOFTREV = "1.0.0"
        self.enabled = False

    def enable(self):
        super().enable()
        self.enabled = True

    def disable(self):
        super().disable()
        self.enabled = False


commLogFileHandler = CommunicationLogFileHandler("log", "h")
commLogFileHandler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
logging.getLogger("communication").addHandler(commLogFileHandler)
logging.getLogger("communication").propagate = False

logging.basicConfig(
    format='%(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.DEBUG)

# Load configuration from config.json
with open("config/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

equipments = {}

# Initialize equipments based on configuration
for equipment_config in config["equipment"]:
    try:
        connect_mode = secsgem.hsms.HsmsConnectMode[equipment_config["connect_mode"]]
    except KeyError:
        print(f"Invalid connect_mode: {equipment_config['connect_mode']}")
        continue

    settings = secsgem.hsms.HsmsSettings(
        address=equipment_config["address"],
        port=equipment_config["port"],
        session_id=equipment_config["session_id"],
        connect_mode=connect_mode,
        device_type=secsgem.common.DeviceType[equipment_config["device_type"]]
    )
    equipment = SampleEquipment(settings)
    equipments[equipment_config["equipment_name"]] = (
        equipment, equipment_config["enable"])

# Enable or disable equipments based on configuration
for equipment, enable in equipments.values():
    if enable:
        equipment.enable()

# Initialize MQTT Handler
mqtt_handler = MQTTHandler(config["mqtt"]["broker"], config["mqtt"]["port"],
                           "some/topic", lambda topic, payload: print(f"Received message: {payload}"))
mqtt_handler.connect()


class HostCmd(cmd.Cmd):
    prompt = "(hostcmd) "

    def do_enable(self, arg):
        equipment_name = arg.strip()
        if equipment_name in equipments:
            equipment, _ = equipments[equipment_name]
            equipment.enable()
            print(f"Equipment {equipment_name} enabled.")
        else:
            print("Invalid equipment name.")

    def do_disable(self, arg):
        equipment_name = arg.strip()
        if equipment_name in equipments:
            equipment, _ = equipments[equipment_name]
            equipment.disable()
            print(f"Equipment {equipment_name} disabled.")
        else:
            print("Invalid equipment name.")

    def do_exit(self, arg):
        print("Exiting...")
        return True

    def do_list(self, arg):
        for equipment_name, (equipment, enable) in equipments.items():
            status = "enabled" if equipment.enabled else "disabled"
            print(f"Equipment {equipment_name}: {status}")


if __name__ == "__main__":
    HostCmd().cmdloop()

    # Disable all equipments before exiting
    for equipment, _ in equipments.values():
        if equipment.enabled:
            equipment.disable()
