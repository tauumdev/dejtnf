import cmd
import ipaddress
import json
import logging
import os

# from secsgem.secs.functionbase import SecsStreamFunction
# from secsgem.secs.functions import secsStreamsFunctions
import src.gem.recipe_manager as recipe
from src.gem.equipment_manager import EquipmentManager

# from secsgem.secs.variables import SecsVarList
# from src.gem.equipment_hsms import Equipment

logger = logging.getLogger("app_logger")


class Config(cmd.Cmd):
    def __init__(self, eq_manager: EquipmentManager):
        super().__init__()
        self.eq_manager = eq_manager
        self.prompt = "config > "

    def emptyline(self):
        """
        Do nothing on empty input line.
        """
        pass

    def do_exit(self, arg: str):
        """
        Exit configuration mode.
        Usage: exit
        """
        return True

    def do_list(self, arg: str):
        """
        List all equipment instances.
        Usage: list
        Sample: list
        """
        print("Listing equipments")
        try:
            equipments = self.eq_manager.list_equipments()
            if not isinstance(equipments, list):
                print(equipments)
                return
            print(json.dumps(equipments, indent=4))
        except Exception as e:
            print(e)

    def do_add(self, arg: str):
        """
        Add a new equipment instance.
        Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <active> <enable>
        Args:
            equipment_name (str): The name of the equipment.
            equipment_model (str): The model of the equipment.
            address (str): The IP address of the equipment.
            port (int): The port of the equipment.
            session_id (int): The session ID of the equipment.
            active (bool): Whether the equipment is active.
            enable (bool): Whether the equipment is enabled.  
        Sample: add TNF-01 192.168.0.1 5000 1 True True          
        """
        print("Adding equipment")
        args = arg.split()
        if len(args) != 7:
            print("Invalid number of arguments")
            print(
                "Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <active> <enable>")
            return
        try:

            equipment_name, equipment_model, address, port, session_id, active, enable = args

            try:
                ipaddress.ip_address(address)
            except ValueError:
                print("Invalid IP address")
                return

            active = active.lower() in ['true', '1', 't', 'y', 'yes']
            enable = enable.lower() in ['true', '1', 't', 'y', 'yes']
            rsp = self.eq_manager.add_equipment(equipment_name, equipment_model, address, int(
                port), int(session_id), active, enable)

            if not isinstance(rsp, bool):
                print(rsp)
                return
            print("Equipment added successfully.", equipment_name)

        except ValueError:
            print("Invalid argument type")
            return

    def do_remove(self, arg: str):
        """
        Remove an equipment instance.
        Usage: remove <equipment_name>
        Sample: remove TNF-01
        """
        print("Removing equipment")
        args = arg.split()
        if len(args) != 1:
            print("Invalid number of arguments")
            print("Usage: remove <equipment_name>")
            return

        try:
            equipment_name = args[0]
            rsp = self.eq_manager.remove_equipment(equipment_name)

            if not isinstance(rsp, bool):
                print(rsp)
                return
            print("Equipment removed successfully.", equipment_name)
        except ValueError:
            print("Invalid argument type")
            return

    def do_edit(self, arg: str):
        """
        Edit and update an equipment instance.
        Usage: edit <equipment_name> <key1=value1> <key2=value2> ...
        Args:
            equipment_name (str): The name of the equipment.
            equipment_model (str): The model of the equipment.
            address (str): The IP address of the equipment.
            port (int): The port of the equipment.
            session_id (int): The session ID of the equipment.
            active (bool): Whether the equipment is active.
            enable (bool): Whether the equipment is enabled.            
        Sample: edit TNF-01 address=192.168.0.1 port=5000
        """
        print("Editing equipment")

        args = arg.split()
        if len(args) < 2:
            print("Invalid number of arguments")
            print(
                "Usage: edit <equipment_name> <key1=value1> <key2=value2> ...")
            return

        try:
            equipment_name = args[0]
            kwargs = {}
            for arg in args[1:]:
                key, value = arg.split('=')
                kwargs[key] = value

            rsp = self.eq_manager.edit_equipment(equipment_name, **kwargs)

            if not isinstance(rsp, bool):
                print(rsp)
                return
            print("Equipment edited successfully.", equipment_name)

        except ValueError:
            logger.error("Invalid argument type")
            return
