import cmd
import logging
from src.core.equipment_manager import EquipmentManager

logger = logging.getLogger("app_logger")


class CommandCli(cmd.Cmd):
    """
    Command line interface for controlling equipment.
    """

    def __init__(self, eq_manager: EquipmentManager):
        """
        Initialize the command line interface with the given equipment manager.

        Args:
            eq_manager (EquipmentManager): The equipment manager instance.
        """
        super().__init__()
        self.eq_manager = eq_manager
        self.prompt = "> "

    def emptyline(self):
        """
        Do nothing on empty input line.
        """
        pass

    def do_list(self, arg: str):
        """
        List all equipments.
        Usage: list
        """
        logger.info(self.eq_manager.list_equipment())

    def do_enable(self, arg: str):
        """
        Enable equipment by name.
        Usage: enable <equipment_name>
        """
        self.eq_manager.enable_equipment(arg)

    def do_disable(self, arg: str):
        """
        Disable equipment by name.
        Usage: disable <equipment_name>
        """
        self.eq_manager.disable_equipment(arg)

    def do_online(self, arg: str):
        """
        Set equipment online by name.
        Usage: online <equipment_name>
        """
        self.eq_manager.online_equipment(arg)

    def do_offline(self, arg: str):
        """
        Set equipment offline by name.
        Usage: offline <equipment_name>
        """
        self.eq_manager.offline_equipment(arg)

    def do_add(self, arg: str):
        """
        Add a new equipment.
        Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <connect_mode> <device_type> <is_enable>
        """
        args = arg.split()
        if len(args) != 8:
            logger.error("Invalid number of arguments for add command.")
            logger.info(
                "Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <connect_mode> <device_type> <is_enable>")
            return
        equipment_name, equipment_model, address, port, session_id, connect_mode, device_type, is_enable = args
        is_enable = is_enable.lower() in ['true', '1', 't', 'y', 'yes']
        self.eq_manager.add_equipment(
            equipment_name, equipment_model, address, int(port), int(session_id), connect_mode, device_type, is_enable)

    def do_remove(self, arg: str):
        """
        Remove an equipment by name.
        Usage: remove <equipment_name>
        """
        self.eq_manager.remove_equipment(arg)

    def do_edit(self, arg: str):
        """
        Edit an existing equipment.
        Usage: edit <equipment_name> <key=value> ...
        """
        args = arg.split()
        if len(args) < 2:
            logger.error("Invalid number of arguments for edit command.")
            logger.info("Usage: edit <equipment_name> <key=value> ...")
            return
        equipment_name = args[0]
        kwargs = {}
        for kv in args[1:]:
            key, value = kv.split("=")
            kwargs[key] = value
        self.eq_manager.edit_equipment(equipment_name, **kwargs)

    def do_clear_event(self, arg: str):
        """
        Clear all collection events by equipment name.
        Usage: clear_cl_event <equipment_name>
        """
        self.eq_manager.clear_collection_event(arg)

    def do_enable_event(self, arg: str):
        """
        Enable event report by equipment name.
        Usage: enable_event <equipment_name> [<ceid1, ceid2, ...>]
        """
        args = arg.split()
        equipment_name = args[0]
        event_id = args[1] if len(args) > 1 else ""
        ceid = list(map(int, event_id.strip('[]').split(','))
                    ) if event_id else []
        self.eq_manager.enable_event_report(equipment_name, ceid)

    def do_subscribe_col(self, arg: str):
        """
        Subscribe to a collection event. by equipment_name.
        Usage: subscribe <equipment_name> <ceid> <dvs1, dvs2, ...> [<report_id>]
        """
        args = arg.split()
        equipment_name = args[0]
        ceid = int(args[1])
        dvs = list(map(int, args[2].strip('[]').split(',')))
        report_id = int(args[3]) if len(args) > 3 else None
        self.eq_manager.subscribe_collection_event(
            equipment_name, ceid, dvs, report_id)

    def do_exit(self, arg: str):
        """
        Exit the program.
        Usage: exit
        """
        self.eq_manager.exit()
        return True
