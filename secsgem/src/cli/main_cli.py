import cmd
import json
from src.cli.control.control_cli import EquipmentControlCli
from src.cli.config.config_cli import EquipmentConfigCli
from src.manager.equipment_manager import EquipmentManager
from src.mqtt.mqtt_client import MqttClient


class CommandCli(cmd.Cmd):
    """
    Command line interface
    """

    def __init__(self, mqtt_client_instant: MqttClient):
        super().__init__()
        self.prompt = "dejtnf >> "
        self.equipments = EquipmentManager(mqtt_client_instant)

    def emptyline(self):
        pass

    def do_list(self, _):
        """
        List equipments
        Usage: list
        """
        equipment_list = self.equipments.list_equipments()
        for equipment in json.loads(equipment_list):
            print(equipment)

    def do_exit(self, _):
        """
        Exit program
        Usage: exit
        """
        self.equipments.exit()
        return True

    def do_config(self, _):
        """
        Equipment configuration command line interface
        Usage: config
        Function: Add, remove, list equipments
        """
        EquipmentConfigCli(self.equipments).cmdloop()

    def do_control(self, equipment_name: str):
        """
        Equipment control command line interface
        Usage: control <equipment_name>
        Function: enable, disable, online, offline, lot_accept, add_lot, subscribe_event, etc.
        """
        equipment = next(
            (eq for eq in self.equipments.equipments if eq.equipment_name == equipment_name), None)

        if not equipment:
            print(f"Equipment {equipment_name} not found")
            print("List equipments to see available equipments")
            print("control <equipment_name>")
            return
        EquipmentControlCli(equipment_name, equipment).cmdloop()

    def do_save(self, _):
        """
        Save equipments to file
        Usage: save
        """
        print(self.equipments.config.save())
