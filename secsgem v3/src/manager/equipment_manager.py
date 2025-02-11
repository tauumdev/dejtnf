
import ipaddress
import json
import secsgem.hsms
from typing import TYPE_CHECKING

from src.gemhost.equipment import Equipment
if TYPE_CHECKING:
    from src.mqtt.mqtt_client import MqttClient


def validate_hsms_settings(equipment):
    """
    Validate hsms settings
    :param equipment: dict
    :return: secsgem.hsms.HsmsSettings
    """
    try:
        address = equipment["address"]
        port = equipment["port"]
        session_id = equipment["session_id"]
        mode = equipment["mode"]

        # Validate address
        if not isinstance(address, str) or not address:
            return ValueError("Invalid address")

        try:
            ipaddress.ip_address(address)
        except ValueError:
            return ValueError("Invalid address")

        # Validate port
        if not isinstance(port, int) or not (0 <= port <= 65535):
            return ValueError("Invalid port")

        # Validate session_id
        if not isinstance(session_id, int) or session_id <= 0:
            return ValueError("Invalid session_id")

        # Validate mode
        if mode not in ["ACTIVE", "PASSIVE"]:
            return ValueError("Invalid mode")

        # Create HsmsSettings object
        setts = secsgem.hsms.HsmsSettings(
            address=address,
            port=port,
            session_id=session_id,
            connect_mode=secsgem.hsms.HsmsConnectMode.ACTIVE if mode == "ACTIVE" else secsgem.hsms.HsmsConnectMode.PASSIVE
        )

        print("HsmsSettings object created successfully")
        return setts

    except KeyError as e:
        return ValueError(f"Missing key: {e}")
    except ValueError as e:
        return ValueError(f"Invalid value: {e}")


class EquipmentManager:

    def __init__(self, mqtt_client_instant: 'MqttClient'):
        self.mqtt_client = mqtt_client_instant
        self.equipments: list[Equipment] = []
        self.mqtt_client.client.user_data_set(
            {"equipments": self.equipments})
        self.load_equipments()

    def load_equipments(self):
        """
        Load equipments from file
        """
        config_path = "files/equipments_cfg.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                equipments_json = json.load(f)
                for equipment in equipments_json.get("equipments", []):

                    settings = validate_hsms_settings(equipment)
                    if isinstance(settings, secsgem.hsms.HsmsSettings):
                        equipment = Equipment(equipment["equipment_name"], equipment["equipment_model"],
                                              True if equipment["enable"] else False, self.mqtt_client, settings)
                        self.equipments.append(equipment)
                        print(
                            f"Equipment {equipment.equipment_name} initialized")
                    else:
                        print(
                            f"Equipment {equipment['equipment_name']} not initialized")
                        print(f"Validation error {settings}")
        except FileNotFoundError:
            print("File not found")
        except Exception as e:
            print(f"Error loading equipments: {e}")

    def save(self):
        """
        Save equipments to file
        :return: str
        """
        config_path = "files/equipments_cfg.json"
        equipments = []
        try:
            for equipment in self.equipments:
                equipments.append({
                    "equipment_name": equipment.equipment_name,
                    "equipment_model": equipment.equipment_model,
                    "address": getattr(equipment.settings, "address", ""),
                    "port": getattr(equipment.settings, "port", "5000"),
                    "session_id": equipment.settings.session_id,
                    "mode": "ACTIVE" if getattr(equipment.settings, "connect_mode") == secsgem.hsms.HsmsConnectMode.ACTIVE else "PASSIVE",
                    "enable": equipment.is_enable
                })

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump({"equipments": equipments}, f, indent=4)
                # print("Equipments saved to file")
                return "Equipments saved to file"
        except Exception as e:
            print(f"Error saving equipments: {e}")
            return f"Error saving equipments: {e}"

    def exit(self):
        """
        Exit program
        """
        print("Exit program.")
        self.save()
        for equipment in self.equipments:
            if equipment.is_connected:
                equipment.secs_control.disable()
        self.mqtt_client.client.loop_stop()
        self.mqtt_client.client.disconnect()

    def add_equipment(self, equipment_name: str, equipment_model: str, enable: bool, settings: secsgem.hsms.HsmsSettings):
        """
        Add equipment
        :param equipment_name: str
        :param equipment_model: str
        :param settings: secsgem.hsms.HsmsSettings
        """
        try:
            settings = validate_hsms_settings(settings)
            if not isinstance(settings, secsgem.hsms.HsmsSettings):
                print(f"Validation error {settings}")
                return f"Validation error {settings}"

            # Check if equipment already exists with name and address
            if next((eq for eq in self.equipments if eq.equipment_name == equipment_name), None):
                print(f"Equipment {equipment_name} already exists")
                return f"Equipment {equipment_name} already exists"
            if next((eq for eq in self.equipments if getattr(eq.settings, "address") == settings.address), None):
                print(
                    f"Equipment with address {settings.address} already exists")
                return f"Equipment with address {settings.address} already exists"
            equipment = Equipment(
                equipment_name, equipment_model, enable, self.mqtt_client, settings)
            self.equipments.append(equipment)
            print(f"Equipment {equipment_name} added")
            self.save()
            return f"Equipment {equipment_name} added"
        except Exception as e:
            print(f"Error adding equipment: {e}")
            return f"Error adding equipment: {e}"

    def remove_equipment(self, equipment_name: str):
        """
        Remove equipment
        :param equipment_name: str
        """
        try:
            equipment = next(
                (eq for eq in self.equipments if eq.equipment_name == equipment_name), None)
            if not equipment:
                print(f"Equipment {equipment_name} not found")
                return f"Equipment {equipment_name} not found"
            self.equipments.remove(equipment)
            print(f"Equipment {equipment_name} removed")
            self.save()
            return f"Equipment {equipment_name} removed"
        except Exception as e:
            print(f"Error removing equipment: {e}")
            return f"Error removing equipment: {e}"

    def list_equipments(self):
        """
        List equipments
        :return: str
        """
        equipments = []
        for equipment in self.equipments:
            equipments.append({
                "equipment_name": equipment.equipment_name,
                "equipment_model": equipment.equipment_model,
                "address": getattr(equipment.settings, "address", ""),
                "port": getattr(equipment.settings, "port", "5000"),
                "session_id": equipment.settings.session_id,
                "mode": "ACTIVE" if getattr(equipment.settings, "connect_mode") == secsgem.hsms.HsmsConnectMode.ACTIVE else "PASSIVE",
                "enable": equipment.is_enable
            })
        return json.dumps(equipments, indent=4)
