import json
import logging
from host.gem_host import DejtnfHost
import secsgem.common
import secsgem.hsms
from mqtt.mqtt_client_wrapper import MQTTClientWrapper

# Initialize the logger
logger = logging.getLogger("app_logger")


class EquipmentManager:
    def __init__(self, equipment_configuration_file):
        self.equipment_config = equipment_configuration_file  # Store the config file path
        self.equipment_list: list[DejtnfHost] = []
        self.mqtt_client = MQTTClientWrapper(self)
        self.mqtt_client.connect("localhost", 1883)
        self.mqtt_client.loop_start()
        self.load_config()

    def load_config(self):
        try:
            with open(self.equipment_config, 'r', encoding='utf-8') as f:
                config = json.load(f)

            for eq in config['equipment']:
                settings = secsgem.hsms.HsmsSettings(
                    address=eq['address'],
                    port=eq['port'],
                    session_id=eq['session_id'],
                    connect_mode=secsgem.hsms.HsmsConnectMode[eq['connect_mode']],
                    device_type=secsgem.common.DeviceType[eq['device_type']]
                )
                eq_obj = DejtnfHost(
                    settings,
                    equipment_name=eq['equipment_name'],
                    equipment_model=eq['equipment_model'],
                    mqtt_client=self.mqtt_client
                )
                if eq['enable']:
                    eq_obj.enable()

                self.equipment_list.append(eq_obj)
                logger.info("Initialized equipment '%s'", eq['equipment_name'])
        except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error("Failed to load config: %s", e)
            exit(1)

    def disable_all_exit(self):
        for eq in self.equipment_list:
            if eq.is_enabled():
                eq.disable()
            eq.mqtt_client.disconnect()
            # logger.info("Disconnecting MQTT broker '%s'", eq.equipment_name)
        logger.info("All equipment disabled.")

    def get_statuses(self):
        statuses = []
        for eq in self.equipment_list:
            status = f"{eq.equipment_name}: {
                'Enabled' if eq.is_enabled() else 'Disabled'}"
            statuses.append(status)
        return statuses

    def online(self, equipment_name):
        for eq in self.equipment_list:
            if eq.equipment_name == equipment_name:
                try:
                    result = eq.go_online()
                    if result == 0:
                        return f"{equipment_name} is now online."
                    elif result == 1:
                        return f"{equipment_name} refused to go online."
                    elif result == 2:
                        return f"{equipment_name} is already online."
                    else:
                        return f"Unknown status for {equipment_name}."
                except Exception as e:
                    logger.error(f"Error bringing {
                                 equipment_name} online: {e}")
                    return f"Failed to bring {equipment_name} online."
        return f"Equipment {equipment_name} not found."

    def offline(self, equipment_name):
        for eq in self.equipment_list:
            if eq.equipment_name == equipment_name:
                try:
                    result = eq.go_offline()
                    if result == 0:
                        return f"{equipment_name} is now offline."
                    elif result == 1:
                        return f"{equipment_name} refused to go offline."
                    elif result == 2:
                        return f"{equipment_name} is already offline."
                    else:
                        return f"Unknown status for {equipment_name}."
                except Exception as e:
                    logger.error(f"Error bringing {
                                 equipment_name} offline: {e}")
                    return f"Failed to bring {equipment_name} offline."
        return f"Equipment {equipment_name} not found."

    def save_equipments_config(self):
        try:
            config = {'equipment': []}
            for eq in self.equipment_list:
                eq_config = {
                    'address': eq.settings.address,
                    'port': eq.settings.port,
                    'session_id': eq.settings.session_id,
                    'connect_mode': eq.settings.connect_mode.name,
                    'device_type': eq.settings.device_type.name,
                    'equipment_name': eq.equipment_name,
                    'equipment_model': eq.equipment_model,
                    'enable': eq.is_enabled()
                }
                config['equipment'].append(eq_config)

            with open(self.equipment_config, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            logger.info("Configuration saved to '%s'", self.equipment_config)
        except Exception as e:
            logger.error("Failed to save config: %s", e)
            return f"Failed to save config: {e}"

    def add_equipment(self, equipment_config):
        try:
            settings = secsgem.hsms.HsmsSettings(
                address=equipment_config['address'],
                port=equipment_config['port'],
                session_id=equipment_config['session_id'],
                connect_mode=secsgem.hsms.HsmsConnectMode[equipment_config['connect_mode']],
                device_type=secsgem.common.DeviceType[equipment_config['device_type']]
            )
            eq_obj = DejtnfHost(
                settings,
                equipment_name=equipment_config['equipment_name'],
                equipment_model=equipment_config['equipment_model'],
                mqtt_client=self.mqtt_client
            )
            if equipment_config['enable']:
                eq_obj.enable()

            self.equipment_list.append(eq_obj)
            logger.info("Added and initialized equipment '%s'",
                        equipment_config['equipment_name'])

            self.save_equipments_config()

            return f"Equipment {equipment_config['equipment_name']} added successfully."
        except KeyError as e:
            logger.error("Failed to add equipment: Missing key %s", e)
            return f"Failed to add equipment: Missing key {e}"
        except Exception as e:
            logger.error("Failed to add equipment: %s", e)
            return f"Failed to add equipment: {e}"
