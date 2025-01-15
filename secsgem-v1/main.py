import cmd
import logging
from src.mqtt.mqtt_client_wrapper import MqttClient
from src.core.equipment_manager import EquipmentManager
from src.cli.command_cli import CommandCli
from src.config.config import EQ_CONFIG_PATH, MQTT_CONFIG_PATH, ENABLE_MQTT
from src.utils.app_logger import AppLogger
from src.utils.gem_logger import CommunicationLogFileHandler
app_logger = AppLogger()
logger = app_logger.get_logger()

# logger.level = logging.WARNING

# Configure communication log file handler
commLogFileHandler = CommunicationLogFileHandler("logs", "h")
commLogFileHandler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))
logging.getLogger("hsms_communication").addHandler(commLogFileHandler)
logging.getLogger("hsms_communication").propagate = False
logging.basicConfig(level=logging.INFO)
# Configure basic logging format and level
# logging.basicConfig(
#     format='%(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.INFO)

mqtt_client = MqttClient(MQTT_CONFIG_PATH)

if __name__ == "__main__":
    logger.info("Starting program...")
    equipment_manager = EquipmentManager(mqtt_client)
    cmd = CommandCli(equipment_manager)
    cmd.cmdloop()
