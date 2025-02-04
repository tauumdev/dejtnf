import logging

from src.cli.main_cli import CommandCli
from src.mqtt.mqtt_client import MqttClient
from src.utils.logger.app_logger import AppLogger

app_logger = AppLogger()
logger = app_logger.get_logger()
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    logger.info("Starting secs/gem dejtnf")

    mqtt_client = MqttClient()
    cli = CommandCli(mqtt_client)
    cli.cmdloop()
