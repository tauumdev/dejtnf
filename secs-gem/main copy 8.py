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
        with open(file_path, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {file_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON in {file_path}: {e}")

    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key in {
                             file_path}: {key}")
    return config


class MqttMessageHandler:

    def on_message(self, client: mqtt.Client, userdata: "EquipmentManager", message: mqtt.MQTTMessage) -> None:
        """
        Handles incoming MQTT messages. Parses the topic and payload to control equipment.
        """
        # Ensure user data is set correctly and includes "equipments"
        if not isinstance(userdata, EquipmentManager):
            logger.error(
                "Invalid userdata. Expected EquipmentManager, got %s.", type(userdata))
            return

        logger.info("Message received on topic %s", message.topic)

        # Decode the message payload
        try:
            payload = message.payload.decode("utf-8").strip()
        except UnicodeDecodeError as e:
            logger.error("Failed to decode message payload: %s", e)
            return

        # Parse the topic structure
        topic_parts = message.topic.split("/")
        if len(topic_parts) == 3 and topic_parts[0] == "equipment" and topic_parts[1] == "control":
            machine_name = topic_parts[2]
            command = payload.lower()

            # Find the corresponding equipment
            equipment = next(
                (eq for eq in userdata.eq_manager if eq.equipment_name == machine_name),
                None
            )

            if equipment:
                logger.info("Processing command '%s' for equipment: %s",
                            command, equipment.equipment_name)

                # Execute the appropriate command
                if command == "online":
                    logger.info("Set equipment '%s' to online.",
                                equipment.equipment_name)
                    userdata.online_equipment(machine_name)
                elif command == "offline":
                    logger.info("Set equipment '%s' to offline.",
                                equipment.equipment_name)
                    userdata.offline_equipment(machine_name)
                elif command == "enable":
                    logger.info("Enabled equipment '%s'.",
                                equipment.equipment_name)
                    userdata.enable_equipment(machine_name)
                elif command == "disable":
                    logger.info("Disabled equipment '%s'.",
                                equipment.equipment_name)
                    userdata.disable_equipment(machine_name)
                else:
                    logger.warning("Unknown command: %s", command)
            else:
                logger.warning(
                    "No equipment found with name '%s'.", machine_name)
        elif len(topic_parts) == 2 and topic_parts[0] == "equipment" and topic_parts[1] == "config":

            command = payload.lower()

            # Execute the appropriate command
            if command == "list":
                client.publish("equipment/response/list/",
                               userdata.list_equipment())

            else:
                logger.warning("Unknown command: %s", command)

        else:
            logger.warning("Invalid topic format: %s", message.topic)


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
        # logger.debug("on_disconnect triggered. Return code: %d", rc)
        if rc == 0:
            logger.info("MQTT connection closed gracefully.")
        else:
            logger.error("MQTT connection closed unexpectedly.")


class Equipment(secsgem.gem.GemHostHandler):
    """
    Represents a single equipment instance.
    """

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


class EquipmentManager:
    """
    Manages a list of equipment instances and initializes them based on a configuration file.
    Attributes:
        equipments (list[Equipment]): A list of equipment instances.
    Args:
        mqtt_client_instance (MqttClient): An instance of the MQTT client to be used by the equipment.
    """

    def __init__(self, mqtt_client_instance: MqttClient):
        self.eq_manager: list[Equipment] = []
        self.mqtt_client = mqtt_client_instance

        with open(EQ_CONFIG_PATH, "r", encoding="utf-8") as f:
            eq_config = json.load(f)
            for config in eq_config.get("equipments", []):
                settings = secsgem.hsms.HsmsSettings(
                    address=config['address'],
                    port=config['port'],
                    session_id=config['session_id'],
                    connect_mode=secsgem.hsms.HsmsConnectMode[config['connect_mode']],
                    device_type=secsgem.common.DeviceType[config['device_type']]
                )
                equipment = Equipment(
                    settings, config["equipment_name"], config["equipment_model"], config["enable"], mqtt_client_instance)

                if equipment.is_enabled:
                    equipment.enable()

                self.eq_manager.append(equipment)
        mqtt_client_instance.client.user_data_set(self)

    def list_equipment(self) -> str:
        """
        List all equipment instances in JSON format.
        Returns:
            str: JSON string of all equipment instances.
        """
        logger.info("Listing all equipment instances.")
        equipment_list = [
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
            for equipment in self.eq_manager
        ]
        return json.dumps(equipment_list, indent=4)

    def enable_equipment(self, equipment_name: str):
        """
        Enable equipment by name.
        Args:
            equipment_name (str): The name of the equipment to enable.
        """
        for equipment in self.eq_manager:
            if equipment.equipment_name == equipment_name:
                try:
                    if equipment.is_enabled:
                        logger.info(
                            "Equipment %s is already enabled.", equipment_name)
                        return
                    else:
                        equipment.enable()
                        equipment.is_enabled = True
                        logger.info("Equipment %s enabled.", equipment_name)
                except Exception as e:
                    logger.error("Error enabling equipment: %s", e)
                return
        logger.info("Equipment %s does not exist.", equipment_name)
        logger.info("Usage: enable %s", "<equipment_name>")
        return

    def disable_equipment(self, equipment_name: str):
        """
        Disable equipment by name.
        Args:
            equipment_name (str): The name of the equipment to disable.
        """
        for equipment in self.eq_manager:
            if equipment.equipment_name == equipment_name:
                try:
                    if not equipment.is_enabled:
                        logger.info(
                            "Equipment %s is already disabled.", equipment_name)
                        return
                    else:
                        equipment.disable()
                        equipment.is_enabled = False
                        logger.info("Equipment %s disabled.", equipment_name)
                except Exception as e:
                    logger.error("Error disabling equipment: %s", e)
                return
        logger.info("Equipment %s does not exist.", equipment_name)
        logger.info("Usage: disable %s", "<equipment_name>")
        return

    def online_equipment(self, equipment_name: str):
        """
        Set equipment online by name.
        Args:
            equipment_name (str): The name of the equipment to set online.
        """
        for equipment in self.eq_manager:
            if equipment.equipment_name == equipment_name:
                try:
                    if equipment.is_enabled:
                        rsp_code = {0x0: "ok", 0x1: "refused",
                                    0x2: "already online"}
                        rsp = equipment.go_online()
                        rsp_msg = rsp_code.get(rsp, "unknown")
                        logger.info("Equipment %s set to online: %s",
                                    equipment_name, rsp_msg)
                        if rsp == 0:
                            return True
                        else:
                            return rsp_msg
                    else:
                        logger.info(
                            "Equipment %s is disabled. Enable it first.", equipment_name)
                        return "equipment disabled"
                except Exception as e:
                    logger.error("Error setting equipment online: %s", e)
                return "error"
        logger.info("Equipment %s does not exist.", equipment_name)
        logger.info("Usage: online %s", "<equipment_name>")
        return "Equipment %s does not exist.", equipment_name

    def offline_equipment(self, equipment_name: str):
        """
        Set equipment offline by name.
        Args:
            equipment_name (str): The name of the equipment to set offline.
        """
        for equipment in self.eq_manager:
            if equipment.equipment_name == equipment_name:
                try:
                    if equipment.is_enabled:
                        rsp_code = {0x0: "ok", 0x1: "refused",
                                    0x2: "already offline"}
                        rsp = equipment.go_offline()
                        rsp_msg = rsp_code.get(rsp, "unknown")
                        logger.info("Equipment %s set to offline: %s",
                                    equipment_name, rsp_msg)
                        if rsp == 0:
                            return True
                        else:
                            return rsp_msg
                    else:
                        logger.info(
                            "Equipment %s is disabled. Enable it first.", equipment_name)
                        return False
                except Exception as e:
                    logger.error("Error setting equipment offline: %s", e)
                return False
        logger.info("Equipment %s does not exist.", equipment_name)
        logger.info("Usage: offline %s", "<equipment_name>")
        return "Equipment % s does not exist.", equipment_name

    def add_equipment(self, equipment_name: str, equipment_model: str, address: str, port: int, session_id: int, connect_mode: str, device_type: str, is_enable: bool):
        """
        Add a new equipment instance.
        Args:
            equipment_name (str): Name of the equipment.
            equipment_model (str): Model of the equipment.
            address (str): IP address for connection.
            port (int): Port for connection.
            session_id (int): Session ID for HSMS communication.
            connect_mode (str): Connection mode ('ACTIVE' or 'PASSIVE').
            device_type (str): Device type.
            is_enable (bool): Whether the equipment is enabled.
        """
        try:
            settings = secsgem.hsms.HsmsSettings(
                address=address,
                port=port,
                session_id=session_id,
                connect_mode=secsgem.hsms.HsmsConnectMode[connect_mode],
                device_type=secsgem.common.DeviceType[device_type]
            )
            new_equipment = Equipment(
                settings, equipment_name, equipment_model, is_enable, self.eq_manager[
                    0].mqtt_client
            )

            if is_enable:
                new_equipment.enable()

            self.eq_manager.append(new_equipment)
            self.save_equipment()
            logger.info("Equipment '%s' added successfully.", equipment_name)
        except Exception as e:
            logger.error("Error adding equipment: %s", e)

    def remove_equipment(self, equipment_name: str):
        """
        Remove an equipment instance by name.
        Args:
            equipment_name (str): Name of the equipment to remove.
        """
        for equipment in self.eq_manager:
            if equipment.equipment_name == equipment_name:
                self.eq_manager.remove(equipment)
                self.save_equipment()
                logger.info("Equipment %s removed.", equipment_name)
                return
        logger.info("Equipment %s does not exist.", equipment_name)
        logger.info("Usage: remove %s", "<equipment_name>")

    def edit_equipment(self, equipment_name: str, **kwargs):
        """
        Edit an existing equipment instance.
        Args:
            equipment_name (str): Name of the equipment to edit.
            kwargs: Key-value pairs of attributes to update.
        """
        for equipment in self.eq_manager:
            if equipment.equipment_name == equipment_name:
                try:
                    for key, value in kwargs.items():
                        if key == "enable":
                            if value.lower() in ['true', '1', 't', 'y', 'yes']:
                                self.enable_equipment(equipment_name)
                            else:
                                self.disable_equipment(equipment_name)
                        elif hasattr(equipment, key):
                            setattr(equipment, key, value)
                            logger.info(
                                "Updated %s for equipment %s to %s.", key, equipment_name, value)
                        elif hasattr(equipment._settings, key):
                            setattr(equipment._settings, key, value)
                            logger.info(
                                "Updated %s for equipment %s to %s.", key, equipment_name, value)
                        else:
                            logger.warning(
                                "Attribute %s not found in equipment %s.", key, equipment_name)
                    self.save_equipment()
                    return
                except Exception as e:
                    logger.error("Error editing equipment: %s", e)
                    return
        logger.info("Equipment %s does not exist.", equipment_name)

    def save_equipment(self):
        """
        Save the current equipment list to the configuration file.
        """
        try:
            config = {"equipments": []}
            for equipment in self.eq_manager:
                config["equipments"].append({
                    "equipment_name": equipment.equipment_name,
                    "equipment_model": equipment.equipment_model,
                    "address": equipment._settings.address,
                    "port": equipment._settings.port,
                    "session_id": equipment._settings.session_id,
                    "connect_mode": equipment._settings.connect_mode.name,
                    "device_type": equipment._settings.device_type.name,
                    "enable": equipment.is_enabled
                })

            with open(EQ_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error("Error saving configuration: %s", e)

    def exit(self):
        """
        Shutdown all equipment instances.
        """
        self.save_equipment()

        for equipment in self.eq_manager:
            try:
                if equipment.is_enabled:
                    equipment.disable()
            except Exception as e:
                logger.error("Error during shutdown: %s", e)

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
        pass

    def do_list(self, arg: str):
        """
        List all equipments.
        Usage: list
        """
        logger.info(self.eq_manager.list_equipment())

    def do_enable(self, arg: str):
        """
        Enable equipment by name.
        Usage: enable <equipment_name>
        """
        self.eq_manager.enable_equipment(arg)

    def do_disable(self, arg: str):
        """
        Disable equipment by name.
        Usage: disable <equipment_name>
        """
        self.eq_manager.disable_equipment(arg)

    def do_online(self, arg: str):
        """
        Set equipment online by name.
        Usage: online <equipment_name>
        """
        self.eq_manager.online_equipment(arg)

    def do_offline(self, arg: str):
        """
        Set equipment offline by name.
        Usage: offline <equipment_name>
        """
        self.eq_manager.offline_equipment(arg)

    def do_add(self, arg: str):
        """
        Add a new equipment.
        Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <connect_mode> <device_type> <is_enable>
        """
        args = arg.split()
        if len(args) != 8:
            logger.info("Invalid number of arguments.")
            logger.info(
                "Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <connect_mode> <device_type> <is_enable>")
            return
        equipment_name, equipment_model, address, port, session_id, connect_mode, device_type, is_enable = args
        is_enable = is_enable.lower() in ['true', '1', 't', 'y', 'yes']
        self.eq_manager.add_equipment(
            equipment_name, equipment_model, address, int(port), int(session_id), connect_mode, device_type, is_enable)

    def do_remove(self, arg: str):
        """
        Remove an equipment by name.
        Usage: remove <equipment_name>
        """
        self.eq_manager.remove_equipment(arg)

    def do_edit(self, arg: str):
        """
        Edit an existing equipment.
        Usage: edit <equipment_name> <key=value> ...
        """
        args = arg.split()
        if len(args) < 2:
            logger.info("Invalid number of arguments.")
            logger.info("Usage: edit <equipment_name> <key=value> ...")
            return
        equipment_name = args[0]
        kwargs = {}
        for kv in args[1:]:
            key, value = kv.split('=')
            kwargs[key] = value
        self.eq_manager.edit_equipment(equipment_name, **kwargs)

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
