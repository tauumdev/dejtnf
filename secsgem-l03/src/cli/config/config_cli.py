from cmd import Cmd
from src.manager.host_manager import SecsGemHostManager
from src.cli.control.control_cli import ControlCli


class ConfigCli(Cmd):
    """
    Command line interface for the configuration of the SECS/GEM Equipment.
    """

    def __init__(self, gem_host_manager: SecsGemHostManager):
        super().__init__()
        self.prompt = "config> "
        self.gem_host_manager = gem_host_manager

    def emptyline(self):
        pass

    def do_return(self, arg):
        """
        Exit the configuration interface
        """
        return True

    def do_add(self, arg):
        """
        Add a SECS/GEM Equipment
        Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <enable> <mode>
        Sample: add EQ1 FCL 192.168.1.10 5000 10 true ACTIVE
        :param equipment_name: str
        :param equipment_model: str
        :param address: str - IP address
        :param port: int - Port number
        :param session_id: int - Session ID
        :param enable: bool - Enable or disable the equipment (enable = True, disable = False)
        :param mode: str - Connection mode (ACTIVE or PASSIVE)
        """
        args = arg.split()
        if len(args) != 7:
            print("Invalid number of arguments")
            print(
                "Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <enable> <mode>")
            return
        equipment_name = args[0]
        equipment_model = args[1]
        address = args[2]
        port = int(args[3])
        session_id = int(args[4])
        enable = True if args[5].lower() == "enable" else False
        mode = args[6]
        self.gem_host_manager.add_equipment(
            equipment_name, equipment_model, enable, address, port, session_id, mode)

    def do_remove(self, equipment_name):
        """
        Remove a SECS/GEM Equipment
        Usage: remove <equipment_name>
        """
        if not equipment_name:
            print("Equipment name is required")
            print("Usage: remove <equipment_name>")
            return

        self.gem_host_manager.remove_equipment(equipment_name)

    def do_list(self, _):
        """
        List equipments
        """
        print(self.gem_host_manager.list_equipments())

    def do_control(self, equipment_name):
        """
        Control equipment
        Usage: control <equipment_name>
        """
        if not equipment_name:
            print("Equipment name is required")
            print("Usage: control <equipment_name>")
            return

        gem_host = next(
            (host for host in self.gem_host_manager.gem_hosts if host.equipment_name == equipment_name), None)

        if not gem_host:
            print(f"Equipment {equipment_name} not found")
            return

        ControlCli(gem_host).cmdloop()
