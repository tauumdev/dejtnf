import cmd
import json
import logging
from typing import TYPE_CHECKING
logger = logging.getLogger("app_logger")

if TYPE_CHECKING:
    from src.equipment_manager.eq_manager import EquipmentManager


class ControlCli(cmd.Cmd):
    """
    Command Line Interface for control of equipment instances
    """

    def __init__(self, eq_manager: "EquipmentManager"):
        super().__init__()
        self.prompt = "control >> "
        self.eq_manager = eq_manager

    def emptyline(self):
        """
        Do nothing on empty line
        """
        return

    def do_return(self, arg):
        """
        Return to main menu
        """
        return True

    def do_list(self, arg):
        """
        List all equipment instances
        Usage: list
        Returns:
            json: List of equipment instances.
        """
        json_str = self.eq_manager.list_equipments()
        logger.info(json.dumps(json_str, indent=4))
        print(json.dumps(json_str, indent=4))

    def do_enable(self, arg):
        """
        Enable equipment instance
        Usage: enable <equipment_name>
        Parameters:
            equipment_name (str): Equipment name.
        """
        logger.info("Enabling equipment...")
        print("\nEnabling equipment...")

        args = arg.split()
        if len(args) != 1:
            logger.error("Invalid number of arguments")
            print("Error: Invalid number of arguments")
            logger.info("Usage: enable <equipment_name>")
            print("Usage: enable <equipment_name>")
            return

        rsp = self.eq_manager.control.enable_equipment(args[0])
        if rsp.get("status") == "success":
            logger.info("Success: Equipment enabled")
            print("Success: Equipment enabled")
        else:
            logger.error("Error: %s", rsp.get('message'))
            print(f"Error: {rsp.get('message')}")

    def do_disable(self, arg):
        """
        Disable equipment instance
        Usage: disable <equipment_name>
        Parameters:
            equipment_name (str): Equipment name.
        """
        logger.info("Disabling equipment...")
        print("\nDisabling equipment...")

        args = arg.split()
        if len(args) != 1:
            logger.error("Invalid number of arguments")
            print("Error: Invalid number of arguments")
            logger.info("Usage: disable <equipment_name>")
            print("Usage: disable <equipment_name>")
            return

        rsp = self.eq_manager.control.disable_equipment(args[0])
        if rsp.get("status") == "success":
            logger.info("Success: Equipment disabled")
            print("Success: Equipment disabled")
        else:
            logger.error("Error: %s", rsp.get('message'))
            print(f"Error: {rsp.get('message')}")

    def do_online(self, arg):
        """
        Set equipment instance online
        Usage: online <equipment_name>
        Parameters:
            equipment_name (str): Equipment name.
        """
        logger.info("Setting equipment online...")
        print("\nSetting equipment online...")

        args = arg.split()
        if len(args) != 1:
            logger.error("Invalid number of arguments")
            print("Error: Invalid number of arguments")
            logger.info("Usage: online <equipment_name>")
            print("Usage: online <equipment_name>")
            return

        rsp = self.eq_manager.control.online_equipment(args[0])
        if rsp.get("status") == "success":
            logger.info("Success: Equipment online")
            print("Success: Equipment online")
        else:
            logger.error("Error: %s", rsp.get('message'))
            print(f"Error: {rsp.get('message')}")

    def do_offline(self, arg):
        """
        Set equipment instance offline
        Usage: offline <equipment_name>
        Parameters:
            equipment_name (str): Equipment name.
        """
        logger.info("Setting equipment offline")
        print("\nSetting equipment offline")
        args = arg.split()
        if len(args) != 1:
            logger.error("Invalid number of arguments")
            print("Error: Invalid number of arguments")
            return
        rsp = self.eq_manager.control.offline_equipment(args[0])
        if rsp.get("status") == "success":
            logger.info("Equipment offline")
            print("Equipment offline")
        else:
            logger.error(rsp.get("message"))
            print(rsp.get("message"))
