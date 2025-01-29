import cmd
import json
import logging
from typing import TYPE_CHECKING

from src.cli.config.config_cli import ConfigCli
from src.cli.control.control_cli import ControlCli

logger = logging.getLogger("app_logger")

if TYPE_CHECKING:
    from src.equipment_manager.eq_manager import EquipmentManager


class Cli(cmd.Cmd):
    """
    Command Line Interface
    """

    def __init__(self, eq_manager: "EquipmentManager"):
        super().__init__()
        self.prompt = ">> "
        self.eq_manager = eq_manager

    def emptyline(self):
        """
        Do nothing on empty line
        """
        pass

    def do_exit(self, arg):
        """
        Exit the program
        """
        logger.info("Exiting program...")
        print("Exiting program...")
        self.eq_manager.exit()
        return True

    def do_list(self, arg):
        """
        List all equipment instances
        """
        json_str = self.eq_manager.list_equipments()
        logger.info(json.dumps(json_str, indent=4))
        print(json.dumps(json_str, indent=4))

    def do_config(self, arg):
        """
        Configuration of equipment instances
        Function to configure equipment instances
        List functions:
            - list: List all equipment instances
            - add: Add new equipment instance
            - remove: Remove equipment instance
            - edit: Edit equipment instance            
        """

        config_cli = ConfigCli(self.eq_manager)
        config_cli.cmdloop()

    def do_control(self, arg):
        """
        Control equipment
        Function to control equipment instances

        """
        control_cli = ControlCli(self.eq_manager)
        control_cli.cmdloop()
