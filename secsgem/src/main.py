import logging
from cli.cli_main import HostCmd
from core.equipment_manager import EquipmentManager
from utils.app_logger import AppLogger

# Setup the logger
app_logger = AppLogger()
logger = app_logger.get_logger()

if __name__ == "__main__":
    logger.info("Starting program...")

    equipment_manager = EquipmentManager("src/config/equipment.json")

    logger.info("Entering CLI mode.")
    cli = HostCmd(equipment_manager)
    cli.cmdloop()

    logger.info("Exiting program.")
