
import ipaddress
import json
import logging
import secsgem.hsms
from src.host.gemhost import SecsGemHost
from typing import TYPE_CHECKING

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

        self.load_equipments_config()

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
        except FileNotFoundError:
            logging.error("Equipments configuration file not found")
        except json.JSONDecodeError:
            logging.error("Equipments configuration file is not a valid JSON")
        except Exception as e:
            logging.error("Error loading equipments configuration: %s", e)

    def exit(self):
        """
        Exit
        """
        for gem_host in self.gem_hosts:
            if gem_host.is_enable:
                gem_host.disable()
                logger.info("Equipment %s disabled", gem_host.equipment_name)
        self.mqtt.client.loop_stop()
        self.mqtt.client.disconnect()

        logger.info("Exiting application")
        print("Exiting application")

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
                "mode": "ACTIVE" if getattr(equipment.settings, "connect_mode") == secsgem.hsms.HsmsConnectMode.ACTIVE else "PASSIVE",
                "enable": equipment.is_enable
            })

        return json.dumps({"equipments": equipments}, indent=4)
