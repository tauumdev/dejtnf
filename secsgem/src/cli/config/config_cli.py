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
    Command Line Interface for configuration of equipment instances
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
        print("Adding equipment")
        args = arg.split()
        if len(args) != 7:
            print("Invalid number of arguments")
            logger.error("Invalid number of arguments")

            logger.info(
                "Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <active> <enable>")
            print(
                "Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <active> <enable>")
            return

        try:
            equipment_name, equipment_model, address, port, session_id, active,  enable = args
            try:
                ipaddress.ip_address(address)
            except ValueError:
                logger.error("Invalid IP address")
                print("Invalid IP address")
                return
            active = active.lower() in ['true', '1', 't', 'y', 'yes']
            enable = enable.lower() in ['true', '1', 't', 'y', 'yes']

            rsp = self.eq_manager.config.add_equipment(equipment_name, equipment_model, address, int(
                port), int(session_id), active, enable)

            if rsp.get("status") == "success":
                print("Equipment added successfully")
                logger.info("Equipment added successfully")
            else:
                logger.error("Error adding equipment")
                print("Error adding equipment")
                logger.error(rsp.get("message"))
                print(rsp.get("message"))
        except Exception as e:
            logger.error("Error adding equipment")
            print("Error adding equipment")
            logger.exception(e)
            print(e)

    def do_remove(self, arg: str):
        """
        Remove an equipment instance.
        Usage: remove <equipment_name>
        Sample: remove TNF-01
        """
        logger.info("Removing equipment")
        print("Removing equipment")
        args = arg.split()
        if len(args) != 1:

            logger.error("Invalid number of arguments")
            print("Invalid number of arguments")
            logger.info("Usage: remove <equipment_name>")
            print("Usage: remove <equipment_name>")
            return

        try:
            equipment_name = args[0]
            # rsp = self.eq_manager.remove_equipment(equipment_name)
            rsp = self.eq_manager.config.remove_equipment(equipment_name)
            if rsp.get("status") == "success":
                logger.info("Equipment removed successfully")
                print("Equipment removed successfully")
            else:
                logger.error("Error removing equipment")
                print("Error removing equipment")
                logger.error(rsp.get("message"))
                print(rsp.get("message"))
        except Exception as e:
            logger.error("Error removing equipment")
            print("Error removing equipment")
            logger.exception(e)
            print(e)

    def do_edit(self, arg: str):
        """
        Edit and update an equipment instance.
        Usage: edit <equipment_name> <key1=value1> <key2=value2> ...
        Args:
            equipment_model (str): The model of the equipment.
            address (str): The IP address of the equipment.
            port (int): The port of the equipment.
            session_id (int): The session ID of the equipment.
            active (bool): Whether the equipment is active.
            enable (bool): Whether the equipment is enabled.            
        Sample: edit TNF-01 address=192.168.0.1 port=5000
        """
        logger.info("Editing equipment")
        print("Editing equipment")

        args = arg.split()
        if len(args) < 2:
            logger.error("Invalid number of arguments")
            print("Invalid number of arguments")
            logger.info(
                "Usage: edit <equipment_name> <key1=value1> <key2=value2> ...")
            print(
                "Usage: edit <equipment_name> <key1=value1> <key2=value2> ...")
            return

        try:
            equipment_name = args[0]
            kwargs = {}
            for arg in args[1:]:
                key, value = arg.split('=')
                kwargs[key] = value

            rsp = self.eq_manager.config.edit_equipment(
                equipment_name, **kwargs)

            if rsp.get("status") == "success":
                logger.info("Equipment updated successfully")
                print("Equipment updated successfully")
            else:
                logger.error("Error edit equipment")
                print("Error edit equipment")
                logger.error(rsp.get("message"))
                print(rsp.get("message"))
        except ValueError:
            logger.error("Invalid argument type")
            print("Invalid argument type")
            return
