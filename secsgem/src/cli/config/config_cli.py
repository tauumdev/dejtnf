import cmd
import ipaddress
import json
import logging
from typing import TYPE_CHECKING
logger = logging.getLogger("app_logger")

if TYPE_CHECKING:
    from src.equipment_manager.eq_manager import EquipmentManager


class ConfigCli(cmd.Cmd):
    """
    Command Line Interface
    """

    def __init__(self, eq_manager: "EquipmentManager"):
        super().__init__()
        self.prompt = "config >> "
        self.eq_manager = eq_manager

    def emptyline(self):
        """
        Do nothing on empty line
        """
        return

    def do_return(self, arg):
        """
        Return main cmd.
        """
        return True

    def do_list(self, arg):
        """
        List all equipment instances
        """
        json_str = self.eq_manager.list_equipments()
        logger.info(json.dumps(json_str, indent=4))

    def do_add(self, arg: str):
        """
        Add new equipment instance
        Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <active> <enable>
        Parameters:
            equipment_name (str): Equipment name.
            equipment_model (str): Equipment model.
            address (str): Equipment IP address.
            port (int): Equipment port number.
            session_id (int): Equipment session ID.
            active (bool): Equipment active status.
            enable (bool): Equipment enable status.
        """
        logger.info("Adding equipment")
        args = arg.split()
        if len(args) != 7:
            logger.error("Invalid number of arguments")
            logger.info(
                "Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <active> <enable>")
            return

        try:
            equipment_name, equipment_model, address, port, session_id, active,  enable = args
            try:
                ipaddress.ip_address(address)
            except ValueError:
                logger.error("Invalid IP address")
                return
            active = active.lower() in ['true', '1', 't', 'y', 'yes']
            enable = enable.lower() in ['true', '1', 't', 'y', 'yes']
            rsp = self.eq_manager.add_equipment(equipment_name, equipment_model, address, int(
                port), int(session_id), active, enable)
            if rsp.get("status") == "success":
                logger.info("Equipment added successfully")
            else:
                logger.error("Error adding equipment")
                logger.error(rsp.get("message"))
        except Exception as e:
            logger.error("Error adding equipment")
            logger.exception(e)
