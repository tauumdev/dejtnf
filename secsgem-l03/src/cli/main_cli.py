from cmd import Cmd

from src.mqtt.mqtt_client import MqttClient
from src.manager.host_manager import SecsGemHostManager

from src.cli.control.control_cli import ControlCli


class MainCli(Cmd):
    """
    MainCli class
    """

    def __init__(self, mqtt_client_instant: MqttClient):
        super().__init__()

        self.prompt = "dejtnf> "
        # self.intro = "Welcome to the SECsGem CLI. Type help or ? to list commands."
        self.mqtt_client = mqtt_client_instant
        self.secs_hosts = SecsGemHostManager(self.mqtt_client)

    def emptyline(self):
        pass

    def do_exit(self, _):
        """
        Exit the Application
        """
        self.secs_hosts.exit()
        return True

    def do_list(self, _):
        """
        List equipments
        """
        print(self.secs_hosts.list_equipments())

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
            (host for host in self.secs_hosts.gem_hosts if host.equipment_name == equipment_name), None)

        if not gem_host:
            print(f"Equipment {equipment_name} not found")
            return

        ControlCli(gem_host).cmdloop()
