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
        print(self.equipment.secs_control.enable())

    def do_disable(self, _):
        """
        Disable equipment
        Usage: disable
        """
        print(self.equipment.secs_control.disable())

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

    def do_get_control_state(self, _):
        """
        Control state
        Usage: control_state
        """
        print(self.equipment.secs_control.get_control_state())

    def do_get_mdln(self, _):
        """
        Get equipment model
        Usage: get_model
        """
        print(self.equipment.mdln)

    def do_get_ppid(self, _):
        """
        Get process program ID
        Usage: get_ppid
        """
        print(self.equipment.ppid)

    def do_req_status(self, svids: str):
        """
        Request equipment status
        Usage: req_status [<svids>]
        Sample: req_status 100,101,102
        """
        svids = [int(svid) for svid in svids.split(",")] if svids else []
        print(self.equipment.secs_control.req_equipment_status(svids))

    def do_req_constant(self, ceids: str):
        """
        Request equipment constant
        Usage: req_constant <ceids>
        Sample: req_constant 100,101,102
        """
        ceids = [int(ceid) for ceid in ceids.split(",")] if ceids else []
        print(self.equipment.secs_control.req_equipment_constant(ceids))

    def do_req_variable_namelist(self, svids: str):
        """
        Request status variable namelist
        Usage: req_status_variable_namelist <svids>
        Sample: req_status_variable_namelist 100,101,102
        """
        svids = [int(svid) for svid in svids.split(",")] if svids else []
        print(self.equipment.secs_control.req_status_variable_namelist(svids))

    def do_req_constant_namelist(self, ecids: str):
        """
        Request equipment constant namelist
        Usage: req_constant_namelist <ecids>
        Sample: req_constant_namelist 100,101,102
        """
        if self.equipment.equipment_model == "FCLX":
            if not ecids:
                print("Invalid arguments")
                print("Usage: req_constant_namelist <ecids>")
                return
            ecids = [int(ecid) for ecid in ecids.split(",")]
            print(self.equipment.secs_control.req_equipment_constant_namelist(ecids))
            return

        ecids = [int(ecid) for ecid in ecids.split(",")] if ecids else []
        print(self.equipment.secs_control.req_equipment_constant_namelist(ecids))

    def do_req_s1f21(self, vids: str):
        """
        Request equipment status
        Usage: req_s1f21 <vids>
        Sample: req_s1f21 100,101,102
        """
        vids = [int(vid) for vid in vids.split(",")] if vids else []
        print(self.equipment.secs_control.req_s1f21(vids))

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
