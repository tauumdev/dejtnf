import json
import logging
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs

from src.gem.equipment_hsms import Equipment
from src.mqtt.mqtt_client_wrapper import MqttClient
from src.config.config import EQ_CONFIG_PATH

logger = logging.getLogger("app_logger")


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

        equipment = Equipment(eq_config["address"], eq_config["port"], eq_config["active"],
                              eq_config["session_id"], eq_config["equipment_name"], eq_config["equipment_model"], eq_config["enable"])

        if equipment.is_enabled:
            equipment.enable()

        self.equipments.append(equipment)
        logger.info("Equipment %s initialized", equipment.equipment_name)

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
                        "active": equipment.active,
                        "session_id": equipment.sessionID,
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
