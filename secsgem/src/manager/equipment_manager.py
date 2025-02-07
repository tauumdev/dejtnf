import json
import logging
from typing import TYPE_CHECKING

from src.utils.config.load_config import load_equipments_config
from src.gemhost.equipment import Equipment
from src.utils.config.app_config import EQUIPMENTS_CONFIG_PATH

if TYPE_CHECKING:
    from src.mqtt.mqtt_client import MqttClient

logger = logging.getLogger("app_logger")


class EquipmentManager:
    """
    Equipment manager
    """

    def __init__(self, mqtt_client_instant: 'MqttClient'):
        self.mqtt_client = mqtt_client_instant
        self.equipments: list[Equipment] = []
        self.config = self.Config(self.equipments)
        self.mqtt_client.client.user_data_set(
            {"equipments": self.equipments})
        self.load_equipments()

    def load_equipments(self):
        equipments_json = load_equipments_config(EQUIPMENTS_CONFIG_PATH)

        for equipment in equipments_json:
            if not isinstance(equipment, dict):
                print("Equipment config file is empty")
                print("Please add equipment configuration to equipments.json")
                print("Type 'config' to add equipment configuration")
                logger.warning("Equipment config file is empty")
                continue
            equipment = Equipment(equipment["equipment_name"], equipment["equipment_model"], equipment["address"],
                                  equipment["port"], equipment["session_id"], equipment["active"], equipment["enable"], self.mqtt_client)

            if equipment.is_enabled:
                print(f"Initializing equipment {equipment.equipment_name}")
                print(equipment.is_enabled)
                equipment.enable()

            self.equipments.append(equipment)
            print(f"Equipment {equipment.equipment_name} initialized")

    def emptyline(self):
        """
        Empty line
        """
        pass

    def exit(self):
        """
        Exit program
        """
        print("Exit program.")
        try:
            self.config.save()
            for equipment in self.equipments:
                try:
                    if equipment.is_enabled:
                        equipment.disable()
                except Exception as e:
                    print(f"Error disabling equipment: {e}")
            self.mqtt_client.client.loop_stop()
            self.mqtt_client.client.disconnect()
        except Exception as e:
            print(f"Error exiting program: {e}")

    def list_equipments(self):
        """
        List equipments
        """
        return json.dumps([{
            "name": equipment.equipment_name,
            "model": equipment.equipment_model,
            "ip": equipment.address,
            "enable": equipment.is_enabled
        } for equipment in self.equipments])

    class Config:
        """
        Equipment configuration
        """

        def __init__(self, equipments: list[Equipment]):
            self.equipments = equipments

        def save(self):
            """
            Save equipments to file
            """
            try:
                with open(EQUIPMENTS_CONFIG_PATH, "w", encoding="utf-8") as f:
                    equipments = {
                        "equipments": [
                            {
                                "equipment_name": equipment.equipment_name,
                                "equipment_model": equipment.equipment_model,
                                "address": equipment.address,
                                "port": equipment.port,
                                "session_id": equipment.sessionID,
                                "active": equipment.active,
                                "enable": equipment.is_enabled
                            } for equipment in self.equipments
                        ]
                    }
                    json.dump(equipments, f, indent=4)
                    logger.info("Equipments saved")
            except Exception as e:
                return {"status": False, "message": f"Error saving equipments: {e}"}
            return {"status": True, "message": "Equipments saved"}

        def add(self, equipment: Equipment):
            """
            Add equipment
            """
            if equipment in self.equipments:
                # print(f"Equipment {equipment.equipment_name} already exists")
                return {"status": False, "message": "Equipment already exists"}
            if any(e.equipment_name == equipment.equipment_name and e.address == equipment.address
                   for e in self.equipments):
                # print(f"Equipment {equipment.name} already exists")
                return {"status": False, "message": "Equipment already exists"}

            if equipment.is_enabled:
                equipment.enable()
            self.equipments.append(equipment)
            self.save()
            return {"status": True, "message": "Equipment added"}

        def remove(self, equipment_name: str):
            """
            Remove equipment
            """
            equipment = next(
                (eq for eq in self.equipments if eq.equipment_name == equipment_name), None)
            if equipment:
                if equipment.is_enabled:
                    return {"status": False, "message": "Equipment is enabled and cannot be removed"}
                self.equipments.remove(equipment)
                self.save()
                return {"status": True, "message": "Equipment removed"}
            else:
                return {"status": False, "message": "Equipment not found"}
