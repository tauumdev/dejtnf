import code
from cmd import Cmd
import logging
import secsgem.hsms
from src.manager.equipment_manager import EquipmentManager
from src.gemhost.equipment import Equipment

from src.utils.logger.app_logger import AppLogger

from src.mqtt.mqtt_client import MqttClient

app_logger = AppLogger()
logger = app_logger.get_logger()
logger.setLevel(logging.INFO)


class EquipmentConfigCli(Cmd):
    """
    Equipment configuration command line interface
    """

    def __init__(self, equipments: EquipmentManager):
        super().__init__()
        self.prompt = "config >> "
        self.equipments = equipments

    def emptyline(self):
        pass

    def do_add(self, arg: str):
        """
        Add equipment
        Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <enable> <mode>
        Sample: add EQ1 FCL true 192.168.1.10 5000 1 ACTIVE
        """
        args = arg.split()
        if len(args) != 7:
            print("Invalid number of arguments")
            print(
                "Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <enable> <mode>")
            return

        equipment_name, equipment_model,  address, port_str, session_id_str, enable_str, mode = args
        enable = enable_str.lower() in ["true", "1", "yes"]

        try:
            port = int(port_str)
            session_id = int(session_id_str)
        except ValueError:
            print("Port and session_id should be integers.")
            return

        settings_dict = {
            "address": address,
            "port": port,
            "session_id": session_id,
            "mode": mode.upper()
        }

        response = self.equipments.add_equipment(
            equipment_name, equipment_model, enable, settings_dict)
        print(response)

    def do_remove(self, equipment_name: str):
        """
        Remove equipment
        Usage: remove <equipment_name>
        """
        self.equipments.remove_equipment(equipment_name)
        print(f"Equipment {equipment_name} removed")

    def do_list(self, _):
        """
        List equipments
        Usage: list
        """
        equipment_list = self.equipments.list_equipments()
        print(equipment_list)

    def do_exit(self, _):
        """
        Exit configuration
        Usage: exit
        """
        return True


class EquipmentControlCli(Cmd):
    """
    Equipment control command line interface
    """

    def __init__(self, equipment: Equipment):
        super().__init__()
        self.prompt = f"{equipment.equipment_name} >> "
        self.equipment = equipment

    def emptyline(self):
        pass

    def do_exit(self, _):
        """
        Exit control
        Usage: exit
        """
        return True

    def do_eq_status(self, _):
        """
        Get equipment status
        Usage: eq_status
        """
        print(self.equipment.secs_control.equipment_status())

    def do_enable(self, _):
        """
        Enable equipment
        Usage: enable
        """
        self.equipment.secs_control.enable()
        print(f"Equipment {self.equipment.equipment_name} enabled")

    def do_disable(self, _):
        """
        Disable equipment
        Usage: disable
        """
        self.equipment.secs_control.disable()
        print(f"Equipment {self.equipment.equipment_name} disabled")

    def do_online(self, _):
        """
        Go online
        Usage: online
        """
        print(self.equipment.secs_control.online())

    def do_offline(self, _):
        """
        Go offline
        Usage: offline
        """
        print(self.equipment.secs_control.offline())

    def do_control_state(self, _):
        """
        Get control state
        Usage: control_state
        """
        control_state = self.equipment.secs_control.control_state()
        print(f"Control state: {control_state}")

    def do_process_state(self, _):
        """
        Get process state
        Usage: process_state
        """
        process_state = self.equipment.secs_control.process_state()
        print(f"Process state: {process_state}")

    def do_select_eq_status_req(self, vids: str):
        """
        S1F3 Select equipment status request
        Usage: select_eq_status_req [<vid>]
        """

        vids = [int(vid) for vid in vids.split(",")] if vids else []
        print(self.equipment.secs_control.select_equipment_status_request(vids))

    def do_stat_var_list_req(self, svids: str):
        """
        S1F11 Get status variable name list request
        Usage: stat_var_list_req [<svid>]
        """

        svids = [int(svid) for svid in svids.split(",")] if svids else []
        print(self.equipment.secs_control.status_variable_namelist_request(svids))

    def do_data_var_list_req(self, dvids: str):
        """
        S1F21 Get data variable name list request
        Usage: data_var_list_req [<dvid>]
        """

        dvids = [int(dvid) for dvid in dvids.split(",")] if dvids else []
        print(self.equipment.secs_control.data_variable_namelist_request(dvids))

    def do_coll_event_list_req(self, ceids: str):
        """
        S1F23 Get collection event name list request
        Usage: coll_event_list_req [<ceid>]
        """

        ceids = [int(ceid) for ceid in ceids.split(",")] if ceids else []
        print(self.equipment.secs_control.collection_event_namelist_request(ceids))

    def do_eq_const_req(self, ecids: str):
        """
        S2F13 Get equipment constant request
        Usage: eq_const_req [<ecid>]
        """

        ecids = [int(ecid) for ecid in ecids.split(",")] if ecids else []
        print(self.equipment.secs_control.equipment_constant_request(ecids))

    def do_eq_const_list_req(self, ecids: str):
        """
        S2F29 Get equipment constant name list request
        Usage: eq_const_list_req [<ecid>]
        """

        ecids = [int(ecid) for ecid in ecids.split(",")] if ecids else []
        print(self.equipment.secs_control.equipment_constant_namelist_request(ecids))

    def do_enable_disable_evt(self, arg: str):
        """
        Enable or disable event
        Usage: enable_disable_evt <enable> [<ceid>]
        Sample: enable_disable_evt true 1,2,3
        """
        args = arg.split()
        if len(args) < 1:
            print("Invalid number of arguments")
            print("Usage: enable_disable_evt <enable> [<ceid>]")
            return

        enable = args[0].lower() in ["true", "1", "yes"]
        ceids = [int(ceid)
                 for ceid in args[1].split(",")] if len(args) > 1 else []
        print(self.equipment.secs_control.enable_disable_event(enable, ceids))

    def do_unsub_all_evt_rpt(self, _):
        """
        Unsubscribe all events report
        Usage: unsub_all_evt_rpt
        """
        print(self.equipment.secs_control.unsubscribe_event_report())

    def do_sub_evt_rpt(self, arg: str):
        """
        Subscribe event report
        Usage: sub_evt_rpt <ceid> <dvs> <report_id>
        Sample: sub_evt_rpt 1 100,101,102 1000
        """
        args = arg.split()
        if len(args) != 3:
            print("Invalid number of arguments")
            print("Usage: sub_evt_rpt <ceid> <dvs> <report_id>")
            return

        ceid, dvs, report_id = args
        dvs = [int(dv) for dv in dvs.split(",")]
        print(self.equipment.secs_control.subscribe_event_report(
            int(ceid), dvs, int(report_id)))


class CommandCli(Cmd):
    def __init__(self, mqtt_client: MqttClient):
        super().__init__()
        self.prompt = "dejtnf >> "
        self.equipments = EquipmentManager(mqtt_client)

    def emptyline(self):
        pass

    def do_exit(self, _):
        """
        Exit program
        Usage: exit
        """
        self.equipments.exit()
        return True

    def do_list(self, _):
        """
        List equipments
        Usage: list
        """
        equipment_list = self.equipments.list_equipments()
        print(equipment_list)

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

        EquipmentControlCli(equipment).cmdloop()


if __name__ == "__main__":
    logger.info("Starting secs/gem dejtnf")

    mqtt_client = MqttClient()

    cli = CommandCli(mqtt_client)
    cli.cmdloop()
