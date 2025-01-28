import json
import logging
from src.equipment_manager.core.load_config import load_equipment_config
from src.equipment_manager.equipment.equipment import Equipment
from src.mqtt.client.mqtt_client import MqttClient

logger = logging.getLogger("app_logger")


class EquipmentManager:
    """
    Class to manage equipment instances.
    """

    def __init__(self, mqtt_client: MqttClient, eq_config_path: str = "files/equipments.json"):
        self.equipments: list[Equipment] = []
        self.mqtt_client = mqtt_client
        self.init_equipments(load_equipment_config(eq_config_path))

    def init_equipments(self, eq_config: json):
        """
        Initialize equipment instances.
        Args:
            eq_config (json): A JSON object containing equipment configurations.
        """
        try:
            for equipment in eq_config.get("equipments", []):
                equipment = Equipment(equipment["equipment_name"], equipment["equipment_model"], equipment["address"],
                                      equipment["port"], equipment["session_id"], equipment["active"], equipment["enable"], self.mqtt_client)

                if equipment.is_enabled:
                    equipment.enable()

                self.equipments.append(equipment)
                logger.info("Equipment %s initialized",
                            equipment.equipment_name)

            self.mqtt_client.client.user_data_set(self)

        except Exception as e:
            logger.error("Error initializing equipment: %s", e)

    def exit(self):
        """
        Exit program.
        """
        self.save_equipments()
        try:
            for equipment in self.equipments:
                try:
                    if equipment.is_enabled:
                        equipment.disable()
                except Exception as e:
                    logger.error("Error while disabling equipment %s: %s",
                                 equipment.equipment_name, e)

            self.mqtt_client.client.loop_stop()
            self.mqtt_client.client.disconnect()
            logger.info("MQTT client stopped.")
        except Exception as e:
            logger.error("Error exiting program: %s", e)

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

    def save_equipments(self, eq_config_path: str = "files/equipments.json"):
        """
        Save equipment configurations to a JSON file.
        Args:
            eq_config_path (str): Path to the JSON file.
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
                    for equipment in self.equipments
                ]
            }

            with open(eq_config_path, "w", encoding="utf-8") as f:
                json.dump(eq_config, f, indent=4)

            logger.info("Equipment configurations saved to %s", eq_config_path)
        except Exception as e:
            logger.error("Error saving equipment configurations: %s", e)

    def add_equipment(self, equipment_name: str, equipment_model: str, address: str, port: int, session_id: int, active: bool,  enable: bool):
        """
        Add a new equipment instance.
        Args:
            equipment_name (str): Equipment name.
            equipment_model (str): Equipment model.
            address (str): Equipment address.
            port (int): Equipment port.
            session_id (int): Equipment session ID.
            active (bool): Equipment active status.            
            enable (bool): Equipment enable status.
        """
        try:
            equipment = Equipment(equipment_name, equipment_model, address,
                                  port, session_id, active, enable, self.mqtt_client)

            if equipment.is_enabled:
                equipment.enable()

            self.equipments.append(equipment)
            self.save_equipments()
            logger.info("Equipment %s added", equipment_name)
            return {"status": "success", "message": f"Equipment {equipment_name} added"}
        except Exception as e:
            logger.error("Error adding equipment: %s", e)
            return {"status": "error", "message": f"Error adding equipment: {e}"}
