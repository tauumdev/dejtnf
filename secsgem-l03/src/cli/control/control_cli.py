from cmd import Cmd
import json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.host.gemhost import SecsGemHost


class ControlCli(Cmd):
    """
    Equipment control command line interface
    """

    def __init__(self, gem_host: 'SecsGemHost'):
        super().__init__()
        self.prompt = f"{gem_host.equipment_name}> "
        self.gem_host = gem_host

    def emptyline(self):
        """
        Empty line
        """
        pass

    def do_exit(self, _):
        """
        Exit control
        """
        return True

    def do_enable(self, _):
        """
        Enable equipment
        """
        print(self.gem_host.secs_control.enable_equipment())

    def do_disable(self, _):
        """
        Disable equipment
        """
        print(self.gem_host.secs_control.disable_equipment())

    def do_req_communication(self, _):
        """
        Request communication
        """
        print(self.gem_host.secs_control.communication_request())

    def do_online(self, _):
        """
        Request online
        """
        print(self.gem_host.secs_control.online_request())

    def do_offline(self, _):
        """
        Request offline
        """
        print(self.gem_host.secs_control.offline_request())

    def do_status(self, _):
        """
        Get equipment status
        """
        print(self.gem_host.secs_control.get_equipment_status())

    def do_get_control_state(self, _):
        """
        Get control state
        Usage: get_control_state
        """
        print(self.gem_host.secs_control.get_control_state())

    def do_get_process_state(self, _):
        """
        Get process state
        Usage: get_process_state
        """
        print(self.gem_host.secs_control.get_process_state())

    def do_get_process_program(self, _):
        """
        Get process program
        Usage: get_process_program
        """
        print(self.gem_host.secs_control.get_process_program())

    # equipment status
    def do_ses_req(self, svid: str):
        """
        S1F3R	Selected Equipment Status Request
        Usage: ses_req [<svid>]
        Sample: ses_req 1,2,3 or ses_req
        """
        svids = [int(s) for s in svid.split(",")] if svid else []
        print(self.gem_host.secs_control.select_equipment_status_request(svids))

    def do_sv_list_req(self, svid: str):
        """
        S1F11R	Status Variable Namelist Request
        Usage: sv_list_req [<svid>]
        Sample: sv_list_req 1,2,3 or sv_list_req
        """
        svids = [int(s) for s in svid.split(",")] if svid else []
        print(self.gem_host.secs_control.status_variable_namelist_request(svids))

    def do_dv_list_req(self, dvid: str):
        """
        S1F21R	Data Variable Namelist Request
        Usage: dv_list_req [<dvid>]
        Sample: dv_list_req 1,2,3 or dv_list_req
        """
        dvids = [int(d) for d in dvid.split(",")] if dvid else []
        print(self.gem_host.secs_control.data_variable_namelist_request(dvids))

    def do_ce_list_req(self, ceid: str):
        """
        S1F23R	Collection Event Namelist Request
        Usage: ce_list_req [<ceid>]
        Sample: ce_list_req 1,2,3 or ce_list_req
        """
        ceids = [int(c) for c in ceid.split(",")] if ceid else []
        response = self.gem_host.secs_control.collection_event_namelist_request(
            ceids)
        if isinstance(response, list):
            print(json.dumps(response, indent=4))
        else:
            print(response)

    def do_ec_req(self, ecid: str):
        """
        S2F13R	Equipment Constant Request
        Usage: ec_req [<ceid>]
        Sample: ec_req 1,2,3 or ec_req
        """
        ceids = [int(c) for c in ecid.split(",")] if ecid else []
        print(self.gem_host.secs_control.equipment_constant_request(ceids))

    def do_ec_list_req(self, ecid: str):
        """
        S2F15R	Equipment Constant Namelist Request
        Usage: ec_list_req [<ceid>]
        Sample: ec_list_req 1,2,3 or ec_list_req
        """
        ceids = [int(c) for c in ecid.split(",")] if ecid else []
        print(self.gem_host.secs_control.equipment_constant_namelist_request(ceids))

    # event and report
    def do_enable_disable_event(self, arg: str):
        """
        S2F37	Enable/Disable Event Report
        Usage: enable_disable_event <enable> [<ceid>]
        Sample: enable_disable_event enable 1,2,3
        """
        args = arg.split()
        if len(args) < 1:
            print("Invalid arguments")
            print("Usage: enable_disable_event <enable> [<ceid>]")
            print("Sample: enable_disable_event enable 1,2,3")
            return

        enable = args[0] == "enable"
        ceid = [int(c) for c in args[1].split(",")] if len(args) > 1 else []

        print(self.gem_host.secs_control.enable_disable_event(enable, ceid))

    def do_define_report(self, arg: str):
        """
        S2F33	Define Report
        Usage: define_report <vids> <report_id>
        Sample: define_report 1,2,3 1000
        """
        args = arg.split()
        if len(args) != 2:
            print("Invalid arguments")
            print("Usage: define_report <vids> <report_id>")
            print("Sample: define_report 1,2,3 validate")
            return
        vids = [int(v) for v in args[0].split(",")]
        report_id = args[1]

        print(self.gem_host.secs_control.define_report(vids, report_id))

    def do_link_event_report(self, arg: str):
        """
        S2F35	Link Event Report
        Usage: link_event_report <ceid> <report_id>
        Sample: link_event_report 1 validate
        """
        args = arg.split()
        if len(args) != 2:
            print("Invalid arguments")
            print("Usage: link_event_report <ceid> <report_id>")
            print("Sample: link_event_report 1 validate")
            return
        ceid = int(args[0])
        report_id = args[1]

        print(self.gem_host.secs_control.link_event_report(ceid, report_id))

    def do_subscribe_report(self, arg: str):
        """
        Subscribe event report
        Usage: sub_evt_rpt <ceid> <dvs> <report_id>
        Sample: sub_evt_rpt 1 100,101,102 1000
        """
        args = arg.split()
        if len(args) != 3:
            print("Invalid arguments")
            print("Usage: sub_evt_rpt <ceid> <dvs> <report_id>")
            print("Sample: sub_evt_rpt 1 100,101,102 1000")
            return
        ceid = int(args[0])
        dvs = [int(d) for d in args[1].split(",")]
        report_id = args[2]
        print(self.gem_host.secs_control.subscribe_event_report(
            ceid, dvs, report_id))

    def do_unsubscribe_report(self, _):
        """
        S2F35	Unsubscribe Report
        Usage: unsub_evt_report
        """
        print(self.gem_host.secs_control.unsubscribe_event_report())

    def do_subscribe_lot_control(self, _):
        """
        Subscribe lot control
        Usage: sub_lot_control
        """
        self.gem_host.secs_control.subscribe_lot_control()

    # process program
