import cmd
import json

from src.gemhost.equipment import Equipment


class EquipmentControlCli(cmd.Cmd):
    """
    Equipment control command line interface
    """

    def __init__(self, equipment_name: str, equipment: Equipment):
        super().__init__()
        self.prompt = f"{equipment_name} >> "
        self.equipment = equipment

    def emptyline(self):
        pass

    def do_return(self, _):
        """
        Return to main menu
        Usage: return
        """
        return True

    def do_status(self, _):
        """
        Equipment status
        Usage: status
        """
        status = self.equipment.secs_control.status()
        print(status)

    # connection management
    def do_enable(self, _):
        """
        Enable equipment
        Usage: enable
        """
        response = self.equipment.secs_control.enable()
        if isinstance(response, dict):
            print(response.get("message"))
            return

    def do_disable(self, _):
        """
        Disable equipment
        Usage: disable
        """
        response = self.equipment.secs_control.disable()
        if isinstance(response, dict):
            print(response.get("message"))
            return

    def do_online(self, _):
        """
        Go online
        Usage: online
        """
        print(self.equipment.secs_control.online().get("message"))

    def do_offline(self, _):
        """
        Go offline
        Usage: offline
        """
        print(self.equipment.secs_control.offline().get("message"))

    def do_control_state(self, _):
        """
        Control state
        Usage: control_state
        """
        print(self.equipment.secs_control.get_control_state())

    def do_process_state(self, _):
        """
        Process state
        Usage: process_state
        """
        response = self.equipment.secs_control.get_process_state()
        if isinstance(response, dict):
            print(response.get("message"))
            return
        print(response)
        # print(self.equipment.secs_control.get_process_state())

    def do_mdln(self, _):
        """
        Get equipment model
        Usage: get_model
        """
        print(self.equipment.mdln)

    def do_ppid(self, _):
        """
        Get process program ID
        Usage: get_ppid
        """
        print(self.equipment.ppid)

    # request equipment status
    def do_select_equipment_status(self, svids: str):
        """
        Select equipment status
        Usage: select_equipment_status [<svids>]
        Sample: select_equipment_status 100,101,102
        """

        svids = [int(svid) for svid in svids.split(",")] if svids else []
        response = self.equipment.secs_control.select_equipment_status_request(
            svids)

        if isinstance(response, dict):
            print(response.get("message"))
            return
        print(response)

    def do_status_variable_namelist(self, svids: str):
        """
        Status variable namelist request
        Usage: status_variable_namelist [<svids>]
        Sample: status_variable_namelist 100,101,102
        """
        svids = [int(svid) for svid in svids.split(",")] if svids else []
        response = self.equipment.secs_control.status_variable_namelist_request(
            svids)
        if isinstance(response, dict):
            print(response.get("message"))
            return
        print(response)

    def do_data_variable_namelist(self, vids: str):
        """
        Data variable namelist request
        Usage: data_variable_namelist [<vids>]
        Sample: data_variable_namelist 100,101,102
        """
        vids = [int(vid) for vid in vids.split(",")] if vids else []
        response = self.equipment.secs_control.data_variable_namelist_request(
            vids)
        if isinstance(response, dict):
            print(response.get("message"))
            return
        print(response)

    # def do_collection_event_namelist(self, ceids: str):
    #     """
    #     Collection event namelist request
    #     Usage: collection_event_namelist [<ceids>]
    #     Sample: collection_event_namelist 100,101,102
    #     """
    #     ceids = [int(ceid) for ceid in ceids.split(",")] if ceids else []
    #     response = self.equipment.secs_control.collection_event_namelist_request(
    #         ceids)
    #     if isinstance(response, dict):
    #         print(response.get("message"))
    #         return
    #     print(response)

    def do_equipment_constant(self, ecids: str):
        """
        Equipment constant request
        Usage: equipment_constant [<ecids>]
        Sample: equipment_constant 100,101,102
        """
        ecids = [int(ecid) for ecid in ecids.split(",")] if ecids else []
        response = self.equipment.secs_control.equipment_constant_request(
            ecids)
        if isinstance(response, dict):
            print(response.get("message"))
            return
        print(response)

    def do_equipment_constant_namelist(self, ecids: str):
        """
        Equipment constant namelist request
        Usage: equipment_constant_namelist [<ecids>]
        Sample: equipment_constant_namelist 100,101,102
        """
        ecids = [int(ecid) for ecid in ecids.split(",")] if ecids else []
        response = self.equipment.secs_control.equipment_constant_namelist_request(
            ecids)
        if isinstance(response, dict):
            print(response.get("message"))
            return
        print(response)

    def do_select_event_report(self, ceids: str):
        """
        Select event report
        Usage: select_event_report <ceids>
        Sample: select_event_report 100,101,102
        """
        if not ceids:
            print("Invalid arguments")
            print("Usage: select_event_report <ceids>")
            return
        ceids = [int(ceid) for ceid in ceids.split(",")]
        response = self.equipment.secs_control.event_report_request(
            ceids)
        if isinstance(response, dict):
            print(response.get("message"))
            return
        print(response)

    # lot management
    def do_lot_accept(self, lot_id: str):
        """
        Accept lot for FCL equipment
        Usage: fcl_lot_accept <lot_id>
        """
        if not lot_id:
            print("Invalid arguments")
            print("Usage: fcl_lot_accept <lot_id>")
            return
        print(self.equipment.secs_control.lot_management.accept_lot_fcl(lot_id))

    def do_add_lot(self, lot_id: str):
        """
        Add lot for FCLX equipment
        Usage: fclx_add_lot <lot_id>
        """
        if not lot_id:
            print("Invalid arguments")
            print("Usage: fclx_add_lot <lot_id>")
            return
        print(self.equipment.secs_control.lot_management.add_lot_fclx(lot_id))

    # event management
    def do_subscribe_event(self, arg: str):
        """
        Subscribe events
        Usage: subscribe_events <ceid> <dvs> [<report_id>]
        Sample: subscribe_events 1000 1,2,3 1005
        """

        args = arg.split()
        if len(args) < 2:
            print("Invalid arguments")
            print("Usage: subscribe_events <ceid> <dvs> [<report_id>]")
            return
        ceid = int(args[0])
        dvs = [int(dv) for dv in args[1].split(",")]
        report_id = int(args[2]) if len(args) > 2 else None

        print(self.equipment.secs_control.subscribe_event(
            ceid, dvs, report_id))

    def do_unsubscribe_event(self, report_id: str):
        """
        Unsubscribe events
        Usage: unsubscribe_events <report_id>
        Sample: unsubscribe_events 1005
        """
        if not report_id:
            print("Invalid arguments")
            print("Usage: unsubscribe_events <report_id>")
            return
        try:
            report_id = int(report_id)
            print(self.equipment.secs_control.unsubscribe_event(report_id))
        except ValueError:
            print("Invalid report_id")
            print("Usage: unsubscribe_events <report_id>")
            return

    def do_unsubscribe_all_events(self, _):
        """
        Unsubscribe all events
        Usage: unsubscribe_all
        """
        print(self.equipment.secs_control.unsubscribe_all_events())

    def do_req_event_report(self, ceid: str):
        """
        Request event report
        Usage: req_event_report <ceid>
        Sample: req_event_report 1000
        """
        if not ceid:
            print("Invalid arguments")
            print("Usage: pp_select <ceid>")
            return
        print(self.equipment.secs_control.req_event_report(ceid))

    # recipe management
    def do_pp_dir(self, _):
        """
        Process program directory
        Usage: pp_dir
        """
        ppid_list = self.equipment.secs_control.recipe_management.pp_dir()
        for ppid in ppid_list:
            print(f"  - {ppid}")

    def do_pp_select(self, ppid: str):
        """
        Select process program
        Usage: pp_select <ppid>
        """
        if not ppid:
            print("Invalid arguments")
            print("Usage: pp_select <ppid>")
            return
        print(self.equipment.secs_control.recipe_management.pp_select(
            ppid).get("message"))

    def do_pp_request(self, ppid: str):
        """
        Requests the process program using the provided Process Program ID (ppid).

        Parameters:
            ppid (str): Process Program Identifier.

        Usage:
            pp_request <ppid>

        Prints:
            The response from the process program request.
        """
        if not ppid:
            print("Invalid arguments")
            print("Usage: pp_request <ppid>")
            return
        print(self.equipment.secs_control.recipe_management.pp_request(ppid))

    def do_pp_send(self, ppid: str):
        """
        Sends the process program using the provided Process Program ID (ppid).

        Parameters:
            ppid (str): Process Program Identifier.

        Usage:
            pp_send <ppid>

        Prints:
            The response message from the process program send operation.
        """
        if not ppid:
            print("Invalid arguments")
            print("Usage: pp_send <ppid>")
            return
        print(self.equipment.secs_control.recipe_management.pp_send(
            ppid))

    def do_pp_delete(self, ppid: str):
        """
        Deletes the process program using the provided Process Program ID (ppid).

        Parameters:
            ppid (str): Process Program Identifier.

        Usage:
            pp_delete <ppid>

        Prints:
            The response from the deletion operation.
        """
        if not ppid:
            print("Invalid arguments")
            print("Usage: pp_delete <ppid>")
            return
        print(self.equipment.secs_control.recipe_management.pp_delete(ppid))

    # STI equipment
    def do_sti_pp_select(self, ppid: str):
        """
        Select process program for STI equipment
        Usage: sti_pp_select <ppid>
        """
        if not ppid:
            print("Invalid arguments")
            print("Usage: sti_pp_select <ppid>")
            return
        self.equipment.secs_control.sti_pp_select(ppid)

    def do_sti_lot_end(self, _):
        """
        End lot for STI equipment
        Usage: sti_lot_end
        """
        self.equipment.secs_control.sti_lot_end()

    def do_sti_go_local(self, _):
        """
        Go local for STI equipment
        Usage: sti_go_local
        """
        self.equipment.secs_control.sti_go_local()
