
import ipaddress
import json
import logging
import os
import requests
import secsgem.hsms
from src.host.gemhost import SecsGemHost
from typing import TYPE_CHECKING
from dotenv import load_dotenv

if TYPE_CHECKING:
    from src.mqtt.mqtt_client import MqttClient

from config.app_config import EQUIPMENTS_CONFIG_PATH


logger = logging.getLogger("app_logger")


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

        # print("HsmsSettings object created successfully")
        return setts

    except KeyError as e:
        return ValueError(f"Missing key: {e}")
    except ValueError as e:
        return ValueError(f"Invalid value: {e}")


class SecsGemHostManager:
    """
    Equipment manager class
    """

    def __init__(self, mqtt_client_instant: 'MqttClient'):
        self.mqtt = mqtt_client_instant
        self.gem_hosts: list[SecsGemHost] = []
        self.mqtt.client.user_data_set({"gem_hosts": self.gem_hosts})

        # self.load_equipments_config()
        self.load_equipments()

    def load_equipments(self):
        """
        Load equipments
        """
        load_dotenv()

        api_server = os.getenv("API_SERVER")
        api_port = int(os.getenv("API_PORT"))
        api_endpoint = os.getenv("API_ENDPOINT")

        # api GET localhost:3000/api/secsgem/equipments?page=1&limit=5&sort=equipment_name&order=1
        # create url
        api_url = f"http://{api_server}:{api_port}/{api_endpoint}/secsgem/equipments?page=1&limit=5&sort=equipment_name&order=1"
        # print(api_url)
        response = requests.get(
            api_url,
            timeout=10,
            headers={'Accept': 'application/json'}
        )
        response.raise_for_status()

        # Validate response format
        equipments = response.json()
        print(equipments)
        # {'docs': [{'_id': '67c700fe403ebe5e10ffb567', 'mode': 'ACTIVE', 'equipment_name': 'TNF-61', 'equipment_model': 'FCL', 'address': '192.168.226.161', 'port': 5000, 'session_id': 61, 'enable': False, 'createdAt': '2025-03-04T13:32:46.731Z', 'updatedAt': '2025-03-15T05:57:19.172Z'}, {'_id': '67d4d1a0018c593bd0645f0a', 'mode': 'ACTIVE', 'equipment_name': 'TNF-62', 'equipment_model': 'FCL', 'address': '192.168.226.162', 'port': 5000, 'session_id': 62, 'enable': False, 'createdAt': '2025-03-15T01:02:24.373Z', 'updatedAt': '2025-03-15T06:01:04.762Z'}, {'_id': '67d4ece4018c593bd0645f4f', 'mode': 'PASSIVE', 'equipment_name': 'TNF-63', 'equipment_model': 'FCL', 'address': '192.168.226.163', 'port': 5000, 'session_id': 63, 'enable': False, 'createdAt': '2025-03-15T02:58:44.546Z', 'updatedAt': '2025-03-15T06:01:13.534Z'}, {'_id': '67d4ed1d018c593bd0645f54', 'mode': 'ACTIVE', 'equipment_name': 'TNF-64', 'equipment_model': 'FCL', 'address': '192.168.226.164', 'port': 5000, 'session_id': 64, 'enable': False, 'createdAt': '2025-03-15T02:59:41.444Z', 'updatedAt': '2025-03-15T04:14:44.446Z'}, {'_id': '67d51922018c593bd06460e0', 'mode': 'ACTIVE', 'equipment_name': 'TNF-65', 'equipment_model': 'FCL', 'address': '192.168.226.165', 'port': 5000, 'session_id': 65, 'enable': False, 'createdAt': '2025-03-15T06:07:30.422Z', 'updatedAt': '2025-03-15T06:14:15.597Z'}], 'totalDocs': 6, 'limit': 5, 'totalPages': 2, 'page': 1, 'pagingCounter': 1, 'hasPrevPage': False, 'hasNextPage': True, 'prevPage': None, 'nextPage': 2}
        if isinstance(equipments, dict):

            for equipment in equipments.get("docs", []):
                setts = validate_hsms_settings(equipment)
                if isinstance(setts, secsgem.hsms.HsmsSettings):
                    gem_host = SecsGemHost(
                        equipment_name=equipment["equipment_name"],
                        equipment_model=equipment["equipment_model"],
                        enable=True if equipment["enable"] else False,
                        mqtt_client=self.mqtt,
                        settings=setts
                    )
                    self.gem_hosts.append(gem_host)
                    logging.info(
                        "Equipment %s loaded successfully", equipment['equipment_name'])
                else:
                    logging.error(
                        "Equipment %s failed to load with error: %s", equipment['equipment_name'], setts)
                    print(
                        f"Equipment {equipment['equipment_name']} not initialized")

    def load_equipments_config(self):
        """
        Load equipments configuration
        """
        try:
            with open(EQUIPMENTS_CONFIG_PATH, 'r', encoding='utf-8') as f:
                equipments = json.load(f)

                for equipment in equipments.get("equipments", []):
                    setts = validate_hsms_settings(equipment)
                    if isinstance(setts, secsgem.hsms.HsmsSettings):
                        gem_host = SecsGemHost(
                            equipment_name=equipment["equipment_name"],
                            equipment_model=equipment["equipment_model"],
                            enable=True if equipment["enable"] else False,
                            mqtt_client=self.mqtt,
                            settings=setts
                        )
                        self.gem_hosts.append(gem_host)
                        logging.info(
                            "Equipment %s loaded successfully", equipment['equipment_name'])
                    else:
                        logging.error(
                            "Equipment %s failed to load with error: %s", equipment['equipment_name'], setts)
                        print(
                            f"Equipment {equipment['equipment_name']} not initialized")
        except FileNotFoundError:
            logging.error("Equipments configuration file not found")
            print("Equipments configuration file not found")
        except json.JSONDecodeError:
            logging.error("Equipments configuration file is not a valid JSON")
            print("Equipments configuration file is not a valid JSON")
        except Exception as e:
            logging.error("Error loading equipments configuration: %s", e)
            print(f"Error loading equipments configuration: {e}")

    def exit(self):
        """
        Exit
        """
        self.save()
        for gem_host in self.gem_hosts:
            if gem_host.is_enable:
                gem_host.disable()
                logger.info("Equipment %s disabled", gem_host.equipment_name)
        self.mqtt.client.loop_stop()
        self.mqtt.client.disconnect()

        logger.info("Exiting application")
        print("Exiting application")

    def save(self):
        """
        Save equipments to file
        :return: str
        """
        equipments = []
        try:
            for equipment in self.gem_hosts:
                equipments.append({
                    "equipment_name": equipment.equipment_name,
                    "equipment_model": equipment.equipment_model,
                    "address": getattr(equipment.settings, "address", ""),
                    "port": getattr(equipment.settings, "port", "5000"),
                    "session_id": equipment.settings.session_id,
                    "mode": getattr(equipment.settings, "connect_mode").name,
                    "enable": equipment.is_enable
                })

            with open(EQUIPMENTS_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"equipments": equipments}, f, indent=4)
                return "Equipments saved to file"
        except Exception as e:
            print(f"Error saving equipments: {e}")
            return f"Error saving equipments: {e}"

    def list_equipments(self):
        """
        List equipments
        """
        equipments = []
        for equipment in self.gem_hosts:
            equipments.append({
                "equipment_name": equipment.equipment_name,
                "equipment_model": equipment.equipment_model,
                "address": getattr(equipment.settings, "address", ""),
                "port": getattr(equipment.settings, "port", "5000"),
                "session_id": equipment.settings.session_id,
                "mode": getattr(equipment.settings, "connect_mode").name,
                "enable": equipment.is_enable
            })

        return json.dumps({"equipments": equipments}, indent=4)

    def add_equipment(self, equipment_name: str, equipment_model: str, enable: bool, address: str, port: int, session_id: int, mode: str):
        # equipment_name, equipment_model, enable, address, port, session_id, mode
        """
        Add equipment
        :param equipment_name: str
        :param equipment_model: str
        :param enable: bool
        :param address: str
        :param port: int
        :param session_id: int
        :param mode: str
        """
        try:
            settings = validate_hsms_settings(
                {"address": address, "port": port, "session_id": session_id, "mode": mode})
            if not isinstance(settings, secsgem.hsms.HsmsSettings):
                print(f"Validation error {settings}")
                return f"Validation error {settings}"

            # Check if equipment already exists with name and address
            if next((eq for eq in self.gem_hosts if eq.equipment_name == equipment_name), None):
                print(f"Equipment {equipment_name} already exists")
                return f"Equipment {equipment_name} already exists"
            if next((eq for eq in self.gem_hosts if getattr(eq.settings, "address") == settings.address), None):
                print(
                    f"Equipment with address {settings.address} already exists")
                return f"Equipment with address {settings.address} already exists"
            equipment = SecsGemHost(
                equipment_name, equipment_model, enable, self.mqtt, settings)
            self.gem_hosts.append(equipment)
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
                (eq for eq in self.gem_hosts if eq.equipment_name == equipment_name), None)
            if not equipment:
                print(f"Equipment {equipment_name} not found")
                return f"Equipment {equipment_name} not found"
            self.gem_hosts.remove(equipment)
            print(f"Equipment {equipment_name} removed")
            self.save()
            return f"Equipment {equipment_name} removed"
        except Exception as e:
            print(f"Error removing equipment: {e}")
            return f"Error removing equipment: {e}"
