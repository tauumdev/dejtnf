import cmd
import json
from src.manager.equipment_manager import EquipmentManager, Equipment
import ipaddress


class EquipmentConfigCli(cmd.Cmd):
    """
    Equipment configuration command line interface
    """

    def __init__(self,  equipments: EquipmentManager):
        super().__init__()
        self.prompt = "config >> "
        self.equipments = equipments

    def emptyline(self):
        pass

    def do_return(self, _):
        """
        Return to main menu
        Usage: return
        """
        return True

    def do_list(self, _):
        """
        List equipments
        Usage: list
        """
        equipment_list = self.equipments.list_equipments()
        for equipment in json.loads(equipment_list):
            print(equipment)

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
        args = arg.split()
        if len(args) != 7:
            print("Invalid arguments")
            print(
                "Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <active> <enable>")
            return

        try:
            equipment_name, equipment_model, address, port, session_id, active,  enable = args
            try:
                ipaddress.ip_address(address)
            except ValueError:
                print("Invalid IP address")
                return
            active = active.lower() in ['true', '1', 't', 'y', 'yes']
            enable = enable.lower() in ['true', '1', 't', 'y', 'yes']

            equipment = Equipment(equipment_name, equipment_model, address,
                                  int(port), int(session_id), active, enable, self.equipments.mqtt_client)

            resp = self.equipments.config.add(equipment)
            if resp.get("status"):
                print(f"Equipment {equipment_name} added")
            else:
                print(f"Error adding equipment: {resp.get('message')}")
        except Exception as e:
            # logger.error("Error adding equipment")
            print("Error adding equipment")
            # logger.exception(e)
            print(e)

    def do_remove(self, equipment_name: str):
        """
        Remove equipment instance
        Usage: remove <equipment_name>
        Parameters:
            equipment_name (str): Equipment name.
        """
        print(self.equipments.config.remove(equipment_name))
