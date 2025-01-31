import logging
from src.utils.config.load_config import load_equipment_config
from src.equipment_manager.equipment.equipment import Equipment
from src.mqtt.client.mqtt_client import MqttClient

from src.equipment_manager.manager.equipment_config import EquipmentConfig
from src.equipment_manager.manager.equipment_control import EquipmentControl

logger = logging.getLogger("app_logger")


class EquipmentManager:
    """
    Class to manage equipment instances.
    """

    def __init__(self, mqtt_client: MqttClient, eq_config_path: str = "files/equipments.json"):
        self.equipments: list[Equipment] = []
        self.mqtt_client = mqtt_client
        self.eq_config_path = eq_config_path

        self.config = EquipmentConfig(self)
        self.control = EquipmentControl(self)

        self.load_equipments(self.eq_config_path)

    def load_equipments(self, eq_path: str):
        """
        Initialize equipment instances.
        Args:
            eq_path (str): Path to the JSON file containing equipment configurations.
        """
        json_data = load_equipment_config(eq_path)
        try:
            for equipment in json_data.get("equipments", []):
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
        self.config.save_equipments()
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
