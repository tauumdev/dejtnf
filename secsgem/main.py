from src.cli.command_cli import Cli
from src.equipment_manager.eq_manager import EquipmentManager
from src.equipment_manager.equipment.equipment import Equipment
from src.mqtt.client.mqtt_client import MqttClient
from src.utils.logger.app_logger import AppLogger

app_logger = AppLogger()
logger = app_logger.get_logger()

if __name__ == "__main__":

    logger.info("Starting program...")

    mqtt_client = MqttClient()
    eq_manager = EquipmentManager(mqtt_client)

    cmd = Cli(eq_manager)
    cmd.cmdloop()
