import ipaddress
import json
import logging
import secsgem.gem
import secsgem.hsms
import secsgem.secs

from src.gem.equipment_hsms import Equipment
from src.mqtt.mqtt_client_wrapper import MqttClient
from src.config.config import EQ_CONFIG_PATH
from src.gem.recipe_manager import get_recipe_store, save_recipe_store
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
        Initialize the equipment manager with the given MQTT client instance.
        Args:
            eq_config (dict): The configuration of the equipment.
        """
        equipment = Equipment(eq_config["address"], eq_config["port"], eq_config["active"],
                              eq_config["session_id"], eq_config["equipment_name"],
                              eq_config["equipment_model"], eq_config["enable"], self.mqtt_client)

        if equipment.is_enabled:
            equipment.enable()

        self.equipments.append(equipment)
        logger.info("Equipment %s initialized", equipment.equipment_name)

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

    # config equipment
    def list_equipments(self):
        """
        List all equipment instances.
        Returns:
            str: A JSON string containing the equipment list.
        """
        logger.info("Listing all equipment instances")
        try:
            equipment_list = [
                {
                    "equipment_name": equipment.equipment_name,
                    "equipment_model": equipment.equipment_model,
                    "address": equipment.address,
                    "port": equipment.port,
                    "session_id": equipment.sessionID,
                    "active": equipment.active,
                    "enable": equipment.is_enabled
                }
                for equipment in self.equipments
            ]

            return equipment_list
        except Exception as e:
            logger.error("Error listing equipment: %s", e)
            return f"Error listing equipment: {e}"

    def add_equipment(self, equipment_name: str, equipment_model: str, address: str, port: int, session_id: int, active: bool,  enable: bool):
        """
        Add a new equipment instance to the equipment list.
        Args:
            equipment_name (str): The name of the equipment.
            equipment_model (str): The model of the equipment.
            address (str): The IP address of the equipment.
            port (int): The port of the equipment.
            session_id (int): The session ID of the equipment.
            active (bool): Whether the equipment is active.
            enable (bool): Whether the equipment is enabled.
        """

        logger.info("Adding a new equipment instance")

        try:

            if any(equipment.equipment_name == equipment_name for equipment in self.equipments):
                return f"Equipment {equipment_name} already exists."

            equipment = Equipment(address, port, active, session_id,
                                  equipment_name, equipment_model, enable, self.mqtt_client)

            self.equipments.append(equipment)
            if enable:
                equipment.enable()

            logger.info("Equipment %s added", equipment.equipment_name)
            self.save_equipment()
            return True

        except Exception as e:
            logger.error("Error adding equipment: %s", e)
            return f"Error adding equipment: {e}"

    def remove_equipment(self, equipment_name: str):
        """
        Remove an equipment instance from the equipment list.
        Args:
            equipment_name (str): The name of the equipment.
        """
        logger.info("Removing equipment %s", equipment_name)
        try:
            for equipment in self.equipments:
                if equipment.equipment_name == equipment_name:
                    if equipment.is_enabled:
                        return f"Equipment {equipment_name} is enabled. Disable it first."
                    self.equipments.remove(equipment)
                    logger.info("Equipment %s removed successfully.",
                                equipment_name)
                    self.save_equipment()
                    return True
            return f"Equipment does not exist. {equipment_name}"
        except Exception as e:
            logger.error("Error removing equipment: %s", e)
            return f"Error removing equipment: {e}"

    def edit_equipment(self, equipment_name: str, **kwargs):
        """
        Edit the attributes of the specified equipment.
        Args:
            equipment_name (str): The name of the equipment.
            kwargs: The attributes to be edited.
        """
        valid_keys = {
            "equipment_name": str,
            "equipment_model": str,
            "address": "ip",  # Special case for IP address validation
            "port": int,
            "session_id": int,
            "active": bool,
            "enable": bool,
        }

        logger.info("Editing equipment %s", equipment_name)
        try:
            for equipment in self.equipments:
                if equipment.equipment_name == equipment_name:
                    for key, value in kwargs.items():

                        if key not in valid_keys:
                            logger.warning("Invalid key: %s", key)
                            return f"Invalid key: {key}"

                        # Validate value type
                        expected_type = valid_keys[key]
                        if expected_type == "ip":
                            try:
                                value = str(ipaddress.ip_address(value))
                            except ValueError:
                                logger.warning("Invalid IP address: %s", value)
                                return f"Invalid IP address: {value}"
                        elif not isinstance(value, expected_type):
                            # Special handling for boolean values provided as strings
                            if expected_type == bool and isinstance(value, str):
                                value = value.lower() in [
                                    'true', '1', 't', 'y', 'yes']
                            elif expected_type == int and isinstance(value, str):
                                try:
                                    value = int(value)
                                except ValueError:
                                    logger.warning(
                                        "Invalid type for %s: Expected %s, got %s", key, expected_type.__name__, type(value).__name__)
                                    return f"Invalid type for {key}: Expected {expected_type.__name__}, got {type(value).__name__}"
                            else:
                                logger.warning("Invalid type for %s: Expected %s, got %s",
                                               key, expected_type.__name__, type(value).__name__)
                                return f"Invalid type for {key}: Expected {expected_type.__name__}, got {type(value).__name__}"

                        if not key == "enable":
                            logger.info("Editing %s: %s -> %s", key,
                                        getattr(equipment, key, None), value)
                            setattr(equipment, key, value)

                        # Handle enable separately
                        if key == "enable":
                            if value:
                                logger.info("Editing %s: %s -> %s",
                                            key, equipment.is_enabled, value)
                                self.enable_equipment(equipment_name)
                            else:
                                logger.info("Editing %s: %s -> %s",
                                            key, equipment.is_enabled, value)
                                self.disable_equipment(equipment_name)

                    logger.info(
                        "Equipment %s edited successfully.", equipment_name)
                    self.save_equipment()
                    return True
            return f"Equipment {equipment_name} does not exist."
        except Exception as e:
            logger.error("Error editing equipment: %s", e)
            return f"Error editing equipment: {e}"

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
                        "address": equipment.address,
                        "port": equipment.port,
                        "session_id": equipment.sessionID,
                        "active": equipment.active,
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

    # control equipment
    def enable_equipment(self, equipment_name: str):
        """
        Enable an equipment instance.
        Args:
            equipment_name (str): The name of the equipment.
        """
        logger.info("Enabling equipment %s", equipment_name)
        try:
            for equipment in self.equipments:
                if equipment.equipment_name == equipment_name:
                    if equipment.is_enabled:
                        logger.info("Equipment %s is already enabled.",
                                    equipment_name)
                        return f"Equipment {equipment_name} is already enabled."
                    equipment.enable()
                    equipment.is_enabled = True
                    logger.info("Equipment %s enabled successfully.",
                                equipment_name)
                    self.save_equipment()
                    return True

            logger.error("Equipment %s does not exist.", equipment_name)
            return f"Equipment {equipment_name} does not exist."
        except Exception as e:
            logger.error("Error enabling equipment: %s", e)
            return f"Error enabling equipment: {e}"

    def disable_equipment(self, equipment_name: str):
        """
        Disable an equipment instance.
        Args:
            equipment_name (str): The name of the equipment.
        """
        logger.info("Disabling equipment %s", equipment_name)
        try:
            for equipment in self.equipments:
                if equipment.equipment_name == equipment_name:
                    if not equipment.is_enabled:
                        logger.info(
                            "Equipment %s is already disabled.", equipment_name)
                        return f"Equipment {equipment_name} is already disabled."
                    equipment.disable()
                    equipment.is_enabled = False
                    logger.info(
                        "Equipment %s disabled successfully.", equipment_name)
                    self.save_equipment()
                    return True

            logger.error("Equipment %s does not exist.", equipment_name)
            return f"Equipment {equipment_name} does not exist."
        except Exception as e:
            logger.error("Error disabling equipment: %s", e)
            return f"Error disabling equipment: {e}"

    def online_equipment(self, equipment_name: str):
        """
        Online an equipment instance.
        Args:
            equipment_name (str): The name of the equipment.
        """
        logger.info("Online equipment %s", equipment_name)
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
        return msg

    def offline_equipment(self, equipment_name: str):
        """
        Offline an equipment instance.
        Args:
            equipment_name (str): The name of the equipment.
        """
        logger.info("Offline equipment %s", equipment_name)
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
        return msg

    # secs control

    def send_remote_command(self, equipment_name: str, rcmd: int | str, params: list[str]):
        """
        Send remote command to the specified equipment.

        Args:
            equipment_name (str): Name of the equipment.
            rcmd (int | str): Remote command ID.
            params (list[str]): List of parameters for the remote command.
        Sample: rcmd TNF-01 1 [["param1", "param2"]]
        """
        logger.info("Sending remote command %s to equipment %s.",
                    rcmd, equipment_name)
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:

                rsp_code = {0x0: "ok,complete", 0x1: "invalid command", 0x2: "cannot do now", 0x3: "parameter error",
                            0x4: "initiated for asynchronous completion", 0x5: "rejected, already in desired condition", 0x6: "invalid object"}
                # Send remote command here
                try:
                    rsp = equipment.send_remote_command(
                        rcmd, params).HCACK.get()

                    rsp_msg = rsp_code.get(rsp, "unknown")

                    if rsp == 0:
                        logger.info(
                            "Remote command %s sent to equipment %s: %s", rcmd, equipment_name, rsp_msg)
                        return True
                    else:
                        logger.info(
                            "Remote command %s sent to equipment %s: %s", rcmd, equipment_name, rsp_msg)
                        return rsp_msg

                except Exception as e:
                    msg = f"Error sending remote command: {e}"
                    logger.error(msg)
                    return msg
        msg = f"Equipment {equipment_name} does not exist."
        logger.info(msg)
        return msg

    def enable_ceids(self, equipment_name: str, ceid: list[int]):
        """
        Enable collection events for the specified equipment.
        Args:
            equipment_name (str): Name of the equipment.
            ceid (list[int]): List of collection event IDs to enable.
        Sample: enable_ceids TNF-01 [1, 2, 3]
        """
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                try:
                    s2f37 = equipment.send_and_waitfor_response(
                        equipment.stream_function(2, 37)(
                            {"CEED": True, "CEID": ceid})
                    )
                    rsp_code = {0x0: "ok", 0x1: "denied"}
                    rsp = equipment.secs_decode(s2f37).get()
                    rsp_msg = rsp_code.get(rsp, "unknown")

                    if rsp == 0:
                        logger.info(
                            "Enabled collection events. %s", equipment_name)
                        return True

                    logger.info(
                        "Error enabling collection events: %s", rsp_msg)
                    return rsp_msg
                except Exception as e:
                    logger.error("Error enabling collection events: %s", e)
                    return "Error enabling collection events: %s", e
        logger.info("Equipment %s does not exist.", equipment_name)
        return f"Equipment does not exist. {equipment_name}"

    def disable_ceids(self, equipment_name: str, ceid: list[int]):
        """
        Disable collection events for the specified equipment.
        Args:
            equipment_name (str): Name of the equipment.
            ceid (list[int]): List of collection event IDs to disable.
        Sample: disable_ceids TNF-01 [1, 2, 3]
        """
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                try:
                    s2f37 = equipment.send_and_waitfor_response(
                        equipment.stream_function(2, 37)(
                            {"CEED": False, "CEID": ceid})
                    )
                    rsp_code = {0x0: "ok", 0x1: "denied"}
                    rsp = equipment.secs_decode(s2f37).get()
                    rsp_msg = rsp_code.get(rsp, "unknown")

                    if rsp == 0:
                        logger.info(
                            "Disabled collection events. %s", equipment_name)
                        return True

                    logger.info(
                        "Error disabling collection events: %s", rsp_msg)
                    return rsp_msg
                except Exception as e:
                    logger.error("Error disabling collection events: %s", e)
                    return "Error disabling collection events: %s", e
        logger.info("Equipment %s does not exist.", equipment_name)
        return f"Equipment does not exist. {equipment_name}"

    def subscribe_collection_event(self, equipment_name, ceid: int | str, dvs: list[int | str], report_id: int | str | None = None):
        """
        Subscribe to collection event.
        Args:
            equipment_name (str): Name of the equipment.
            ceid (int | str): Collection event ID.
            dvs (list[int | str]): List of device IDs.
            report_id (int | str | None): Report ID.
        Sample: subscribe_collection_event TNF-01 1001 [1, 2, 3] 1001    
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
        return f"Equipment does not exist. {equipment_name}"

    def disable_ceid_report(self, equipment_name: str):
        """
        Disable all Collection Event Reports.
        """
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                try:
                    s2f34 = equipment.disable_ceid_reports()
                    rsp_code = {0x0: "ok",
                                0x1: "out of space",
                                0x2: "invalid format",
                                0x3: "1 or more RPTID already defined",
                                0x4: "1 or more invalid VID"}
                    rsp = equipment.secs_decode(s2f34).get()
                    rsp_msg = rsp_code.get(rsp, "unknown")

                    if rsp == 0:
                        logger.info(
                            "Disabled collection events. %s", equipment_name)
                        return True

                    logger.info(
                        "Error disabling collection events: %s", rsp_msg)
                    return rsp_msg
                except Exception as e:
                    logger.error("Error disabling collection events: %s", e)
                    return "Error disabling collection events: %s", e
        logger.info("Equipment %s does not exist.", equipment_name)
        return f"Equipment does not exist. {equipment_name}"

    def send_recipe_to_equipment(self, equipment_name: str, recipe_name: str):
        """
        Send recipe to the specified equipment.
        Args:
            equipment_name (str): Name of the equipment.
            recipe_name (str): Recipe to send.
        Sample: send_recipe TNF-01 "RECIPE"
        """
        logger.info("Sending recipe to equipment %s.", equipment_name)
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                try:
                    recipe_data = get_recipe_store(equipment_name, recipe_name)
                    if "error" in recipe_data:
                        return recipe_data["error"]

                    ppbody = secsgem.secs.variables.SecsVarBinary(
                        recipe_data["recipe_data"])
                    s7f4 = equipment.send_and_waitfor_response(
                        equipment.stream_function(7, 3)(
                            {"PPID": recipe_name, "PPBODY": ppbody})
                    )

                    decode_s7f4 = equipment.secs_decode(s7f4)
                    print(decode_s7f4.__dir__)
                    rsp_code = {0x0: "Accepted", 0x1: "Permission not granted", 0x2: "length error", 0x3: "matrix overflow",
                                0x4: "PPID not found", 0x5: "unsupported mode", 0x6: "initiated for asynchronous completion", 0x7: "storage limit error"}

                    if decode_s7f4.get() == 0:
                        logger.info("Recipe sent successfully.")
                        return True
                    logger.info("Error sending recipe: %s", rsp_code.get(
                        decode_s7f4.get(), "unknown"))
                    return rsp_code.get(decode_s7f4.get(), "unknown")
                except Exception as e:
                    logger.error("Error sending recipe: %s", e)
                    return "Error sending recipe: %s", e
        logger.info("Equipment %s does not exist.", equipment_name)
        return f"Equipment does not exist. {equipment_name}"

    def request_recipe_from_equipment(self, equipment_name: str, recipe_name: str = None):
        """
        Request recipe from the specified equipment.
        Args:
            equipment_name (str): Name of the equipment.
            recipe_name (str): Recipe to request.
            Sample: request_recipe TNF-01 "RECIPE"
        Usage: request_recipe <equipment_name> [<recipe_name>]  
        Returns:
            - Recipe data if recipe_name is provided
            - Recipe list if recipe_name is not provided  
        """
        logger.info("Requesting recipe from equipment %s.", equipment_name)
        for equipment in self.equipments:
            if equipment.equipment_name == equipment_name:
                try:
                    if recipe_name:
                        s7f6 = equipment.send_and_waitfor_response(
                            equipment.stream_function(7, 5)(recipe_name)
                        )

                        decode_s7f6 = equipment.secs_decode(s7f6)
                        ppid, ppbody = decode_s7f6

                        if ppid.get() is None or ppbody.get() is None:
                            logger.error(
                                "Received null ppbody from equipment %s", equipment_name)
                            return f"Received null from equipment : {equipment_name}"

                        save_recipe_store(
                            equipment_name, ppid.get(), ppbody.get())
                        return True
                    else:
                        s7f20 = equipment.send_and_waitfor_response(
                            equipment.stream_function(7, 19)()
                        )
                        decode_s7f20 = equipment.secs_decode(s7f20).get()
                        return decode_s7f20

                except Exception as e:
                    logger.error("Error requesting recipe: %s", e)
                    return "Error requesting recipe: %s", e
        logger.info("Equipment %s does not exist.", equipment_name)
        return f"Equipment does not exist. {equipment_name}"
