import logging
# from src.manager.host_manager import SecsGemHostManager
from src.mqtt.mqtt_client import MqttClient
from config.logger.all_logger import AppLogger
from src.cli.main_cli import MainCli

app_logger = AppLogger()
logger = app_logger.get_logger()
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    print("Applicaiton started")
    logger.info("Applicaiton started")

    mqtt_client = MqttClient()

    cli = MainCli(mqtt_client)
    cli.cmdloop()
