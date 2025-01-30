import json
import logging
import ipaddress
from typing import TYPE_CHECKING

from src.equipment_manager.equipment.equipment import Equipment

if TYPE_CHECKING:
    from src.equipment_manager.eq_manager import EquipmentManager

logger = logging.getLogger("app_logger")


class EquipmentConfig:
    """
    This class handles the configuration of equipment, including saving, adding, removing, and editing equipment instances.
    """

    def __init__(self, manager: 'EquipmentManager'):
        self.manager = manager

    def save_equipments(self):
        """
        Save equipment configurations to a JSON file.
        """
        try:
            eq_config = {
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
                    for equipment in self.manager.equipments
                ]
            }

            with open(self.manager.eq_config_path, "w", encoding="utf-8") as f:
                json.dump(eq_config, f, indent=4)

            logger.info(
                "Equipment configurations saved to files/equipments.json")
        except Exception as e:
            logger.error("Error saving equipment configurations: %s", e)

    def validate_equipment_data(self, equipment_data):
        """
        Validate equipment data before adding.
        Args:
            equipment_data (dict): Equipment details.
        Returns:
            dict: Validation result.
        """
        valid_keys = {
            "equipment_name": str,
            "equipment_model": str,
            "address": "ip",
            "port": int,
            "session_id": int,
            "active": bool,
            "enable": bool,
        }

        for key, expected_type in valid_keys.items():
            value = equipment_data.get(key)

            # Validate IP address separately
            if expected_type == "ip":
                try:
                    ipaddress.ip_address(value)
                except ValueError:
                    return {"status": "error", "message": f"Invalid IP address: {value}"}

            # Validate integer values
            elif expected_type == int:
                if not isinstance(value, int):
                    return {"status": "error", "message": f"{key} must be an integer"}
                if key == "port" and (value < 1 or value > 65535):
                    return {"status": "error", "message": f"Invalid port number: {value}"}

            # Validate boolean values
            elif expected_type == bool:
                if not isinstance(value, bool):
                    return {"status": "error", "message": f"{key} must be a boolean"}

            # Validate string values
            elif expected_type == str:
                if not isinstance(value, str) or not value.strip():
                    return {"status": "error", "message": f"{key} must be a non-empty string"}

        return {"status": "success"}

    def add_equipment(self, equipment_name: str, equipment_model: str, address: str, port: int, session_id: int, active: bool, enable: bool):
        """
        Add a new equipment instance with validation.
        Args:
            equipment_name (str): Equipment name.
            equipment_model (str): Equipment model.
            address (str): Equipment IP address.
            port (int): Equipment port number.
            session_id (int): Equipment session ID.
            active (bool): Equipment active status.
            enable (bool): Equipment enable status.
        """
        # Create equipment data dictionary
        equipment_data = {
            "equipment_name": equipment_name,
            "equipment_model": equipment_model,
            "address": address,
            "port": port,
            "session_id": session_id,
            "active": active,
            "enable": enable
        }

        # Validate input data
        validation_result = self.validate_equipment_data(equipment_data)
        if validation_result["status"] == "error":
            return validation_result  # Return validation error immediately

        try:
            # Check if equipment already exists
            if any(equipment.equipment_name == equipment_name for equipment in self.manager.equipments):
                return {"status": "error", "message": f"Equipment {equipment_name} already exists"}

            # Check if the IP address is already in use
            if any(equipment.address == address for equipment in self.manager.equipments):
                return {"status": "error", "message": f"IP address {address} is already assigned to another equipment"}

            # Create Equipment instance
            equipment = Equipment(equipment_name, equipment_model, address,
                                  port, session_id, active, enable, self.manager.mqtt_client)

            # Enable if necessary
            if equipment.is_enabled:
                equipment.enable()

            # Add to manager's equipment list
            self.manager.equipments.append(equipment)
            self.save_equipments()
            logger.info("Equipment %s added", equipment_name)
            return {"status": "success", "message": f"Equipment {equipment_name} added"}

        except Exception as e:
            logger.error("Error adding equipment: %s", e)
            return {"status": "error", "message": f"Error adding equipment: {e}"}

    def remove_equipment(self, equipment_name: str):
        """
        Remove an equipment instance.
        Args:
            equipment_name (str): Equipment name.
        """
        try:
            for equipment in self.manager.equipments:
                if equipment.equipment_name == equipment_name:
                    if equipment.is_enabled:
                        return {"status": "error", "message": f"Equipment {equipment_name} is enabled. Disable it first."}
                    self.manager.equipments.remove(equipment)
                    self.save_equipments()
                    logger.info("Equipment %s removed", equipment_name)
                    return {"status": "success", "message": f"Equipment {equipment_name} removed"}

            logger.error("Equipment %s not found", equipment_name)
            return {"status": "error", "message": f"Equipment {equipment_name} not found"}
        except Exception as e:
            logger.error("Error removing equipment: %s", e)
            return {"status": "error", "message": f"Error removing equipment: {e}"}

    def edit_equipment(self, equipment_name_: str, **kwargs):
        """
        Edit the attributes of the specified equipment.
        Args:
            equipment_name (str): The name of the equipment.
            kwargs: The attributes to be edited.
        """
        if "equipment_name" in kwargs:
            return {"status": "error", "message": "Modifying equipment_name is not allowed"}

        valid_keys = {
            "equipment_model": str,
            "address": "ip",  # Special case for IP address validation
            "port": int,
            "session_id": int,
            "active": bool,
            "enable": bool,
        }

        try:
            for equipment in self.manager.equipments:
                if equipment.equipment_name == equipment_name_:
                    for key, value in kwargs.items():
                        # if key == "equipment_name":
                        #     return {"status": "error", "message": f"equipment_name is not alow to change"}
                        if key not in valid_keys:
                            logger.warning("Invalid key: %s", key)
                            return {"status": "error", "message": f"Invalid key: {key}"}

                        # Validate value type
                        expected_type = valid_keys[key]
                        if expected_type == "ip":
                            try:
                                value = str(ipaddress.ip_address(value))
                            except ValueError:
                                logger.warning("Invalid IP address: %s", value)
                                return {"status": "error", "message": f"Invalid IP address: {value}"}

                            # Check for duplicate IP address
                            for existing_equipment in self.manager.equipments:
                                if existing_equipment.address == value and existing_equipment.equipment_name != equipment_name_:
                                    logger.warning(
                                        "IP address %s already exists for another equipment.", value)
                                    return {"status": "error", "message": f"IP address {value} already exists for another equipment."}

                        elif not isinstance(value, expected_type):
                            # Special handling for boolean values provided as strings
                            if expected_type == bool and isinstance(value, str):
                                value = value.lower() in [
                                    'true', '1', 't', 'y', 'yes']
                            elif expected_type == int and isinstance(value, str):
                                try:
                                    value = int(value)
                                except ValueError:
                                    return {"status": "error", "message": f"Invalid type for {key}: Expected {expected_type.__name__}, got {type(value).__name__}"}
                            else:
                                return {"status": "error", "message": f"Invalid type for {key}: Expected {expected_type.__name__}, got {type(value).__name__}"}

                        if not key == "enable":
                            logger.info("Editing %s: %s -> %s", key,
                                        getattr(equipment, key, None), value)
                            setattr(equipment, key, value)

                        # Handle enable separately
                        if key == "enable":
                            if value:
                                if equipment.is_enabled:
                                    return {"status": "error", "message": f"Equipment {equipment_name_} is already enabled."}
                                equipment.enable()
                            else:
                                if not equipment.is_enabled:
                                    return {"status": "error", "message": f"Equipment {equipment_name_} is already disabled."}
                                equipment.disable()
                    logger.info(
                        "Equipment %s edited successfully.", equipment_name_)
                    self.save_equipments()
                    return {"status": "success", "message": f"Equipment {equipment_name_} edited successfully."}
            return {"status": "error", "message": f"Equipment {equipment_name_} not found"}
        except Exception as e:
            logger.error("Error editing equipment: %s", e)
            return {"status": "error", "message": f"Error editing equipment: {e}"}
