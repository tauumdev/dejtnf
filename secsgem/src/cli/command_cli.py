import cmd
import json
import logging
from typing import TYPE_CHECKING
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
        self.eq_manager.exit()
        return True

    def do_list(self, arg):
        """
        List all equipment instances
        """
        json_str = self.eq_manager.list_equipments()
        logger.info(json.dumps(json_str, indent=4))

    def do_config(self, arg):
        """
        Configuration
        """
        from src.cli.config.config_cli import ConfigCli
        cmd = ConfigCli(self.eq_manager)
        cmd.cmdloop()
