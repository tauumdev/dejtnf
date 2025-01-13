import cmd
import json
import logging

import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs

import paho.mqtt.client as mqtt

from src.utils.gem_logger import CommunicationLogFileHandler
from src.utils.app_logger import AppLogger
from src.config.config import EQ_CONFIG_PATH, MQTT_CONFIG_PATH, ENABLE_MQTT

app_logger = AppLogger()
logger = app_logger.get_logger()

# Configure communication log file handler
commLogFileHandler = CommunicationLogFileHandler("logs", "h")
commLogFileHandler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
logging.getLogger("communication").addHandler(commLogFileHandler)
logging.getLogger("communication").propagate = False

# Configure basic logging format and level
logging.basicConfig(
    format='%(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.INFO)


def load_config(file_path: str, required_keys: list[str]) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("Config file not found:%s", file_path)
    except json.JSONDecodeError as e:
        raise ValueError("Failed to parse JSON in %s:%s", file_path, e)

    for key in required_keys:
        if key not in config:
            raise ValueError(
                "Missing required config key in %s:%s", file_path, key)
    return config


class MqttMessageHandler:

    def on_message(self, client: mqtt.Client, eq_manager: "EquipmentManager", message: mqtt.MQTTMessage) -> None:

        # Ensure user data is set correctly and includes "equipments"
        if not isinstance(eq_manager, EquipmentManager):
            logger.error(
                "Invalid eq_manager. Expected EquipmentManager, got %s.", type(eq_manager))
            client.publish("equipment/response/error",
                           "Invalid equipment manager.")
            return

        logger.info("Message received on topic %s", message.topic)

        # Decode the message payload
        try:
            payload = message.payload.decode("utf-8").strip()
        except UnicodeDecodeError as e:
            logger.error("Failed to decode message payload: %s", e)
            client.publish("equipment/response/error",
                           "Failed to decode message payload.")
            return

        # Parse the topic structure
        topic_parts = message.topic.split("/")
        if len(topic_parts) == 3 and topic_parts[0] == "equipment" and topic_parts[1] == "control":
            machine_name = topic_parts[2]
            command = payload.lower()

            # Find the corresponding equipment
            equipment = next(
                (eq for eq in eq_manager.equipments if eq.equipment_name == machine_name),
                None
            )

            if equipment:
                rsp_topic_control = "equipment/response/control/" + machine_name + "/" + command

                logger.info("Processing command '%s' for equipment: %s",
                            command, equipment.equipment_name)

                # Execute the appropriate command
                if command == "online":
                    logger.info("Set equipment '%s' to online.",
                                equipment.equipment_name)
                    rsp = eq_manager.online_equipment(machine_name)
                    client.publish(rsp_topic_control, rsp)
                elif command == "offline":
                    logger.info("Set equipment '%s' to offline.",
                                equipment.equipment_name)
                    rsp = eq_manager.offline_equipment(machine_name)
                    client.publish(rsp_topic_control, rsp)
                elif command == "enable":
                    logger.info("Enabled equipment '%s'.",
                                equipment.equipment_name)
                    rsp = eq_manager.enable_equipment(machine_name)
                    client.publish(rsp_topic_control, rsp)
                elif command == "disable":
                    logger.info("Disabled equipment '%s'.",
                                equipment.equipment_name)
                    rsp = eq_manager.disable_equipment(machine_name)
                    client.publish(rsp_topic_control, rsp)
                else:
                    logger.warning("Unknown command: %s", command)
                    client.publish(rsp_topic_control,
                                   f"Unknown command. {command}")

            else:
                logger.warning("Equipment %s not found.", machine_name)
                client.publish(rsp_topic_control, f"Equipment {
                               machine_name} not found.")

        elif len(topic_parts) == 2 and topic_parts[0] == "equipment" and topic_parts[1] == "config":
            command = payload.lower()
            rsp_topic_config = "equipment/response/config/" + command
            # Execute the appropriate command
            if command == "list":
                logger.info(eq_manager.list_equipment())
                client.publish(rsp_topic_config, eq_manager.list_equipment())
            else:
                logger.warning("Unknown command: %s", command)
                client.publish(rsp_topic_config, f"Unknown command. {command}")
        else:
            logger.warning("Invalid topic format: %s", message.topic)
            client.publish("equipment/response/error",
                           f"Invalid topic format: {message.topic}")


class MqttClient:

    def __init__(self, config_path):

        self.client = mqtt.Client()
        self.client.enable_logger(logger)
        self.client.on_connect = self.on_connect
        self.client.on_message = MqttMessageHandler().on_message
        self.client.on_disconnect = self.on_disconnect

        if ENABLE_MQTT:
            self.load_config(config_path)

    def load_config(self, config_path):

        try:
            logger.info("Initializing MQTT client...")
            config = load_config(
                config_path, ["broker", "port", "username", "password", "keepalive"])
            self.client.username_pw_set(config["username"], config["password"])
            self.client.connect(
                config["broker"], config["port"], keepalive=config.get("keepalive", 60))
            self.client.loop_start()
            logger.info("MQTT loop started.")
        except Exception as e:
            logger.error("Failed to initialize MQTT client: %s", e)
            raise

    def close(self):

        try:
            self.client.disconnect()
            self.client.loop_stop()
            logger.info("MQTT client disconnected and loop stopped.")
        except Exception as e:
            logger.error("Error during MQTT client shutdown: %s", e)

    def on_connect(self, client, userdata, flags, rc):

        if rc == 0:
            self.client.subscribe("equipment/control/#")
            self.client.subscribe("equipment/config/#")
            logger.info(
                "MQTT connection established. Subscribed to %s",  "equipment/control/#")
        else:
            logger.error(
                "Failed to connect to MQTT broker. Return code: %d", rc)

    def on_disconnect(self, client, userdata, rc):

        if rc == 0:
            logger.info("MQTT connection closed gracefully.")
        else:
            logger.error("MQTT connection closed unexpectedly.")


class Equipment(secsgem.gem.GemHostHandler):

    def __init__(self, settings: secsgem.common.Settings, equipment_name: str, equipment_model: str, is_enable: bool, mqtt_client: MqttClient):

        super().__init__(settings)
        self.equipment_name = equipment_name
        self.equipment_model = equipment_model
        self.is_enabled = is_enable
        self.MDLN = "dejtnf"
        self.SOFTREV = "1.0.1"

        self._protocol.events.disconnected += self.on_connection_closed

        self.mqtt_client = mqtt_client

    def _on_communicating(self, _):
        """
        Logs the communication state of the equipment.
        """
        logger.info("%s Communication state: _on_communicating",
                    self.equipment_name)
        return super()._on_communicating(_)

    def _on_state_communicating(self, _):
        """
        Logs the communication state of the equipment.
        """
        logger.info("%s Communication state: _on_state_communicating",
                    self.equipment_name)
        return super()._on_state_communicating(_)

    def on_connection_closed(self, _):
        """
        Logs the communication state of the equipment.
        """
        logger.info("%s Communication state: on_connection_closed",
                    self.equipment_name)
        return super().on_connection_closed(_)

    def send_remote_command(self, rcmd, params):
        try:
            return super().send_remote_command(rcmd, params)
        except Exception as e:
            logger.error("Error sending remote command '%s': %s", rcmd, e)
            raise

    def _on_s06f11(self, handler, message):

        print("S06F11 received")

        rsp = self.send_remote_command(
            rcmd="LOT_ACCEPT", params=[["LotID", "123456"]])
        print(rsp.get())
        return super()._on_s06f11(handler, message)


class EquipmentManager:

    def __init__(self, mqtt_client_instance: MqttClient):

        self.equipments: list[Equipment] = []
        self.mqtt_client = mqtt_client_instance

        with open(EQ_CONFIG_PATH, "r", encoding="utf-8") as f:
            eq_configs = json.load(f)
            for eq_config in eq_configs.get("equipments", []):
                # Initialize equipment instances here
                self.init_equipment(eq_config)

        mqtt_client_instance.client.user_data_set(self)

    def init_equipment(self, eq_config: dict):

        settings = secsgem.hsms.HsmsSettings(
            address=eq_config['address'],
            port=eq_config['port'],
            session_id=eq_config['session_id'],
            connect_mode=secsgem.hsms.HsmsConnectMode[eq_config['connect_mode']],
            device_type=secsgem.common.DeviceType[eq_config['device_type']]
        )
        equipment = Equipment(
            settings, eq_config["equipment_name"], eq_config["equipment_model"], eq_config["enable"], self.mqtt_client)

        if equipment.is_enabled:
            equipment.enable()

        self.equipments.append(equipment)
        logger.info("Equipment '%s' initialized successfully.",
                    eq_config["equipment_name"])

    def save_equipment(self):
        """
        Save the current equipment list to the configuration file.
        """
        try:
            # Save the equipment list to the configuration file here
            eq_configs = {
                "equipments": [
                    {
                        "equipment_name": equipment.equipment_name,
                        "equipment_model": equipment.equipment_model,
                        "address": equipment._settings.address,
                        "port": equipment._settings.port,
                        "session_id": equipment._settings.session_id,
                        "connect_mode": equipment._settings.connect_mode.name,
                        "device_type": equipment._settings.device_type.name,
                        "enable": equipment.is_enabled
                    }
                    for equipment in self.equipments
                ]
            }
            with open(EQ_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(eq_configs, f, indent=4)
            logger.info("Equipment list saved successfully.")
            return True
        except Exception as e:
            logger.error("Error saving equipment: %s", e)
            return "Error saving equipment: %s", e

    def send_rcmd(self, equipment_name: str, rcmd: str, params: list[list[str]]) -> str:
        """
        Send a remote command to the specified equipment.
        """
        equipment = next(
            (eq for eq in self.equipments if eq.equipment_name == equipment_name),
            None
        )

        if equipment:
            try:
                rsp = equipment.send_remote_command(rcmd, params)
                return rsp
            except Exception as e:
                logger.error("Error sending remote command: %s", e)
                return "Error sending remote command: %s", e
        else:
            logger.error("Equipment %s not found.", equipment_name)
            return f"Equipment {equipment_name} not found."

    def exit(self):
        """
        Shutdown all equipment instances.
        """
        self.save_equipment()

        for equipment in self.equipments:
            # Shutdown the equipment here
            try:
                if equipment.is_enabled:
                    equipment.disable()
            except Exception as e:
                logger.error("Error disabling equipment: %s", e)
                return "Error disabling equipment: %s", e

        self.mqtt_client.close()

        return True


class CommandCli(cmd.Cmd):
    """
    Command line interface for controlling equipment.
    """

    def __init__(self, eq_manager: EquipmentManager):

        super().__init__()
        self.eq_manager = eq_manager
        self.prompt = "> "

    def emptyline(self):
        """
        Do nothing on empty input line.
        """
        pass

    def do_sendrcmd(self, arg: str):
        """
        Send a remote command to the specified equipment.
        Usage: sendrcmd <equipment_name> <rcmd> <params>
        """

        rcmd = "LOT_ACCEPT"
        params = [["LotID", "123456"]]
        rsp = self.eq_manager.send_rcmd("TNF-61", rcmd, params)
        print(rsp)
        return True

    def do_exit(self, arg: str):
        """
        Exit the program.
        Usage: exit
        """
        self.eq_manager.exit()
        return True


mqtt_client = MqttClient(MQTT_CONFIG_PATH)

if __name__ == "__main__":
    logger.info("Starting program...")

    equipment_manager = EquipmentManager(mqtt_client)
    cmd = CommandCli(equipment_manager)
    cmd.cmdloop()
