import cmd
import logging
from src.core.equipment_manager import EquipmentManager

logger = logging.getLogger("app_logger")


class CommandCli(cmd.Cmd):
    def __init__(self, eq_manager: EquipmentManager):
        super().__init__()
        self.eq_manager = eq_manager
        self.prompt = "> "

    def emptyline(self):
        """
        Do nothing on empty input line.
        """
        pass

    def do_exit(self, arg: str):
        """
        Exit the program.
        Usage: exit
        """
        self.eq_manager.exit()

        return True
