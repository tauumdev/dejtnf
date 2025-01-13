import json
import logging
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs

from src.gemhsms.equipment_hsms import Equipment
from src.mqttclient.mqtt_client_wrapper import MqttClient

from src.config.config import EQ_CONFIG_PATH

logger = logging.getLogger("app_logger")


class EquipmentManager:
    """
    Manages a list of equipment instances and initializes them based on a configuration file.

    Attributes:
        equipments (list[Equipment]): A list of equipment instances.

    Args:
        mqtt_client_instance (MqttClient): An instance of the MQTT client to be used by the equipment.
    """

    def __init__(self, mqtt_client_instance: MqttClient):
        """
        Initialize the equipment manager with the given MQTT client instance.

        Args:
            mqtt_client_instance (MqttClient): The MQTT client instance.
        """
        self.equipments: list[Equipment] = []
        self.mqtt_client = mqtt_client_instance

        with open(EQ_CONFIG_PATH, "r", encoding="utf-8") as f:
            eq_configs = json.load(f)
            for eq_config in eq_configs.get("equipments", []):
                # Initialize equipment instances here
                self.init_equipment(eq_config)

        mqtt_client_instance.client.user_data_set(self)

    def init_equipment(self, eq_config: dict):
        """
        Initialize equipment instances based on the configuration file.
        """
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
            for equipment in self.equipments
        ]
        return json.dumps(equipment_list, indent=4)

    def enable_equipment(self, equipment_name: str):
        """
        Enable equipment by name.

        Args:
            equipment_name (str): The name of the equipment to enable.
        """
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                # Enable the equipment here
                try:
                    if equipment.is_enabled:
                        msg = f"Equipment {
                            equipment_name} is already enabled."
                        logger.info(msg)
                        return msg
                    else:
                        equipment.enable()
                        equipment.is_enabled = True
                        msg = f"Equipment {equipment_name} enabled."
                        logger.info(msg)
                        return True
                except Exception as e:
                    msg = f"Error enabling equipment: {e}"
                    logger.error(msg)
                    return msg
        msg = f"Equipment {equipment_name} does not exist."
        logger.info(msg)
        logger.info("Usage: enable %s", "<equipment_name>")
        return msg

    def disable_equipment(self, equipment_name: str):
        """
        Disable equipment by name.

        Args:
            equipment_name (str): The name of the equipment to disable.
        """
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                # Disable the equipment here
                try:
                    if not equipment.is_enabled:
                        msg = f"Equipment {
                            equipment_name} is already disabled."
                        logger.info(msg)
                        return msg
                    else:
                        equipment.disable()
                        equipment.is_enabled = False
                        msg = f"Equipment {equipment_name} disabled."
                        logger.info(msg)
                        return True
                except Exception as e:
                    msg = f"Error disabling equipment: {e}"
                    logger.error(msg)
                    return msg
        msg = f"Equipment {equipment_name} does not exist."
        logger.info(msg)
        logger.info("Usage: disable %s", "<equipment_name>")
        return msg

    def online_equipment(self, equipment_name: str):
        """
        Set equipment online by name.

        Args:
            equipment_name (str): The name of the equipment to set online.

        Returns:
            bool or str: True if the equipment is set online successfully, otherwise an error message.
        """
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                # Set the equipment online here
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
                        msg = f"Equipment {
                            equipment_name} is disabled. Enable it first."
                        logger.info(msg)
                        return msg
                except Exception as e:
                    msg = f"Error setting equipment online: {e}"
                    logger.error(msg)
                    return msg
        msg = f"Equipment {equipment_name} does not exist."
        logger.info(msg)
        logger.info("Usage: online %s", "<equipment_name>")
        return msg

    def offline_equipment(self, equipment_name: str):
        """
        Set equipment offline by name.

        Args:
            equipment_name (str): The name of the equipment to set offline.

        Returns:
            bool or str: True if the equipment is set offline successfully, otherwise an error message.
        """
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                # Set the equipment offline here
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
                        msg = f"Equipment {
                            equipment_name} is disabled. Enable it first."
                        logger.info(msg)
                        return msg
                except Exception as e:
                    msg = f"Error setting equipment offline: {e}"
                    logger.error(msg)
                    return msg
        msg = f"Equipment {equipment_name} does not exist."
        logger.info(msg)
        logger.info("Usage: offline %s", "<equipment_name>")
        return msg

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
                settings, equipment_name, equipment_model, is_enable, self.equipments[
                    0].mqtt_client
            )

            if is_enable:
                # Enable the new equipment here
                new_equipment.enable()

            self.equipments.append(new_equipment)
            self.save_equipment()
            logger.info("Equipment '%s' added successfully.", equipment_name)
            return True
        except Exception as e:
            logger.error("Error adding equipment: %s", e)
            return "Error adding equipment: %s", e

    def remove_equipment(self, equipment_name: str):
        """
        Remove an equipment instance by name.

        Args:
            equipment_name (str): Name of the equipment to remove.
        """
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                # Remove the equipment here
                self.equipments.remove(equipment)
                self.save_equipment()
                logger.info("Equipment %s removed successfully.",
                            equipment_name)
                return True
        logger.info("Equipment %s does not exist.", equipment_name)
        logger.info("Usage: remove %s", "<equipment_name>")
        return "Equipment %s does not exist.", equipment_name

    def edit_equipment(self, equipment_name: str, **kwargs):
        """
        Edit an existing equipment instance.

        Args:
            equipment_name (str): Name of the equipment to edit.
            kwargs: Key-value pairs of attributes to update.
        """
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                # Edit the equipment attributes here
                try:
                    for key, value in kwargs.items():
                        if key == "equipment_name":
                            equipment.equipment_name = value
                        elif key == "equipment_model":
                            equipment.equipment_model = value
                        elif key == "address":
                            equipment._settings.address = value
                        elif key == "port":
                            equipment._settings.port = int(value)
                        elif key == "session_id":
                            equipment._settings.session_id = int(value)
                        elif key == "connect_mode":
                            equipment._settings.connect_mode = secsgem.hsms.HsmsConnectMode[value]
                        elif key == "device_type":
                            equipment._settings.device_type = secsgem.common.DeviceType[value]
                        elif key == "is_enable":
                            is_enable = value.lower() in [
                                'true', '1', 't', 'y', 'yes']
                            if is_enable:
                                equipment.enable()
                            else:
                                equipment.disable()
                            equipment.is_enabled = is_enable
                        else:
                            logger.warning("Unknown key: %s", key)
                    self.save_equipment()
                    logger.info(
                        "Equipment %s edited successfully.", equipment_name)
                    return True
                except Exception as e:
                    logger.error("Error editing equipment: %s", e)
                return "Error editing equipment: %s", e
        logger.info("Equipment %s does not exist.", equipment_name)
        return "Equipment %s does not exist.", equipment_name

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

    ########################################################

    def send_remote_command(self, equipment_name: str, rcmd: int | str, params: list[str]):
        """
        Send remote command to the specified equipment.

        Args:
            equipment_name (str): Name of the equipment.
            rcmd (int | str): Remote command ID.
            params (list[str]): List of parameters for the remote command.
        """
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                # Send remote command here
                try:
                    equipment.send_remote_command(rcmd, params)
                    logger.info(
                        "Remote command %s sent to equipment %s.", rcmd, equipment_name)
                    return True
                except Exception as e:
                    msg = f"Error sending remote command: {e}"
                    logger.error(msg)
                    return msg
        msg = f"Equipment {equipment_name} does not exist."
        logger.info(msg)
        logger.info("Usage: send_remote_command %s",
                    "<equipment_name> <rcmd> <params>")
        return msg

    def clear_collection_event(self, equipment_name: str):
        """
        Clear collection event for the specified equipment.

        Args:
            equipment_name (str): Name of the equipment.
        """
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                # Clear collection event here
                try:
                    equipment.clear_collection_events()
                    logger.info(
                        "Collection event for equipment %s cleared.", equipment_name)
                    return True
                except Exception as e:
                    logger.error("Error clearing collection event: %s", e)
                    return "Error clearing collection event: %s", e
        logger.info("Equipment %s does not exist.", equipment_name)
        logger.info("Usage: clear %s", "<equipment_name>")
        return "Equipment %s does not exist.", equipment_name

    def enable_event_report(self, equipment_name: str, ceid: list[int]):
        """
        Enable event report for the specified equipment.

        Args:
            equipment_name (str): Name of the equipment.
            ceid (list[int]): List of collection event IDs to enable.
        """
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                # Enable event report here
                try:
                    secs_message = {"CEED": True, "CEID": ceid}
                    equipment.send_and_waitfor_response(
                        equipment.stream_function(2, 37)(secs_message))
                    logger.info(
                        "Event report for equipment %s enabled. ceid: %s", equipment_name, ceid if ceid else "all")
                    return True
                except Exception as e:
                    logger.error("Error enabling event report: %s", e)
                    return "Error enabling event report: %s", e
        logger.info("Equipment %s does not exist.", equipment_name)
        logger.info("Usage: enable_event_report %s", "<equipment_name> <ceid>")
        return "Equipment %s does not exist.", equipment_name

    def subscribe_collection_event(self, equipment_name, ceid: int | str, dvs: list[int | str], report_id: int | str | None = None):
        """
        Subscribe to collection event.
        """
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                try:
                    equipment.subscribe_collection_event(ceid, dvs, report_id)
                    logger.info("Collection event subscribed successfully.")
                    return True
                except Exception as e:
                    logger.error("Error subscribing collection event: %s", e)
                    return "Error subscribing collection event: %s", e
        logger.info("Equipment %s does not exist.", equipment_name)
    ########################################################

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
