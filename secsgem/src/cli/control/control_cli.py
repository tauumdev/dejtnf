from cmd import Cmd
import json
import shlex

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

    def do_return(self, _):
        """
        Exit control
        """
        return True

    def do_connect(self, _):
        """
        Connect equipment
        """
        print(self.gem_host.secs_control.enable_equipment())

    def do_disconnect(self, _):
        """
        Disconnect equipment
        """
        print(self.gem_host.secs_control.disable_equipment())

    def do_req_communication(self, _):
        """
        Request communication
        """
        print(self.gem_host.secs_control.communication_request())

    def do_are_you_there(self, _):
        """
        Are you there
        """
        print(self.gem_host.are_you_there())

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
    def do_req_svs(self, svid: str):
        """
        S1F3R	Selected Equipment Status Request
        Usage: req_ses [<svid>]
        Sample: req_ses 1,2,3 or req_ses
        """
        svids = [int(s) for s in svid.split(",")] if svid else []
        print(self.gem_host.secs_control.select_equipment_status_request(svids))

    def do_req_list_svs(self, svid: str):
        """
        S1F11R	Status Variable Namelist Request
        Usage: req_list_svs [<svid>]
        Sample: req_list_svs 1,2,3 or req_list_svs
        """
        svids = [int(s) for s in svid.split(",")] if svid else []
        print(self.gem_host.secs_control.status_variable_namelist_request(svids))

    def do_req_list_dvs(self, dvid: str):
        """
        S1F21R	Data Variable Namelist Request
        Usage: req_list_dvs [<dvid>]
        Sample: req_list_dvs 1,2,3 or req_list_dvs
        """
        dvids = [int(d) for d in dvid.split(",")] if dvid else []
        print(self.gem_host.secs_control.data_variable_namelist_request(dvids))

    def do_req_list_ces(self, ceid: str):
        """
        S1F23R	Collection Event Namelist Request
        Usage: req_list_ces [<ceid>]
        Sample: req_list_ces 1,2,3 or req_list_ces
        """
        ceids = [int(c) for c in ceid.split(",")] if ceid else []
        response = self.gem_host.secs_control.collection_event_namelist_request(
            ceids)
        if isinstance(response, list):
            print(json.dumps(response, indent=4))
        else:
            print(response)

    def do_req_ecs(self, ecid: str):
        """
        S2F13R	Equipment Constant Request
        Usage: req_ecs [<ceid>]
        Sample: req_ecs 1,2,3 or req_ecs
        """
        ceids = [int(c) for c in ecid.split(",")] if ecid else []
        print(self.gem_host.secs_control.equipment_constant_request(ceids))

    def do_req_list_ecs(self, ecid: str):
        """
        S2F15R	Equipment Constant Namelist Request
        Usage: req_list_ecs [<ceid>]
        Sample: req_list_ecs 1,2,3 or req_list_ecs
        """
        ceids = [int(c) for c in ecid.split(",")] if ecid else []
        print(self.gem_host.secs_control.equipment_constant_namelist_request(ceids))

    def do_set_ec(self, arg: str):
        """
        S2F15	Set Equipment Constant
        Usage: set_ec <ceid> <vid> <value>
        Sample: set_ec 1 100 200
        """
        args = arg.split()
        if len(args) != 2:
            print("Invalid arguments")
            print("Usage: set_ec <ceid> <value>")
            print("Sample: set_ec 1 200")
            return
        ceid = int(args[0])
        value = args[1]

        eac = {0: "ok", 1: "one or more constants does not exist",
               2: "busy", 3: "one or more values out of range"}
        response_code = self.gem_host.set_ec(ceid, value)
        print(eac[response_code])

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

    # lot management
    def do_accept_lot(self, arg: str):
        """
        Accept lot
        Usage: accept_lot <lot_id>
        """
        if not arg:
            print("Invalid arguments")
            print("Usage: accept_lot <lot_id>")
            return
        print(self.gem_host.secs_control.accept_lot(arg))

    def do_reject_lot(self, arg: str):
        """
        Reject lot
        Usage: reject_lot <lot_id>
        """
        if not arg:
            print("Invalid arguments")
            print("Usage: reject_lot <lot_id>")
            return
        print(self.gem_host.secs_control.reject_lot(arg))

    def do_add_lot_fclx(self, arg: str):
        """
        Add lot
        Usage: add_lot <lot_id>
        """
        if not arg:
            print("Invalid arguments")
            print("Usage: add_lot <lot_id>")
            return
        print(self.gem_host.secs_control.add_lot_fclx(arg))

    def do_reject_lot_fclx(self, arg: str):
        """
        Reject lot
        Usage: reject_lot <lot_id> <reason>
        """
        args = arg.split()
        if len(args) != 2:
            print("Invalid arguments")
            print("Usage: reject_lot <lot_id> <reason>")
            return
        print(self.gem_host.secs_control.reject_lot_fclx(args[0], args[1]))

    # recipe management
    def do_pp_dir(self, _):
        """
        Process Program Directory
        Usage: pp_dir
        """
        print(self.gem_host.secs_control.pp_list())

    def do_pp_inquire(self, arg: str):
        """
        Process Program Inquire
        Usage: pp_inquire <pp_id>
        """
        if not arg:
            print("Invalid arguments")
            print("Usage: pp_inquire <pp_id>")
            return
        print(self.gem_host.secs_control.pp_load_inquire(arg))

    def do_pp_send(self, arg: str):
        """
        Process Program Send
        Usage: pp_send <pp_id>
        """
        if not arg:
            print("Invalid arguments")
            print("Usage: pp_send <pp_id>")
            return
        print(self.gem_host.secs_control.pp_send(arg))

    def do_pp_request(self, arg: str):
        """
        Process Program Request
        Usage: pp_request <pp_id>
        """
        if not arg:
            print("Invalid arguments")
            print("Usage: pp_request <pp_id>")
            return

        self.gem_host.secs_control.pp_request(arg)

    def do_pp_delete(self, arg: str):
        """
        Process Program Delete
        Usage: pp_delete <pp_id>
        Sample: pp_delete A,B,1
        """
        # ppid as list
        if not arg:
            print("Invalid arguments")
            print("Usage: pp_delete <pp_id>")
            return

        ppids = [p for p in arg.split(",")]

        print(self.gem_host.secs_control.pp_delete(ppids))

    def do_pp_select(self, arg: str):
        """
        Process Program Select
        Usage: pp_select <pp_id>
        """
        if not arg:
            print("Invalid arguments")
            print("Usage: pp_select <pp_id>")
            return
        print(self.gem_host.secs_control.pp_select(arg))

    # remote command
    def do_send_remote_command(self, arg: str):
        """
        Send remote command
        Usage: send_remote_command <rcmd> <cpname1> <cpval1> [<cpname2> <cpval2> ...]
        Sample: send_remote_command PP-SELECT PPName1 SOIC PPName2 LQFP
                send_remote_command STOP
                send_remote_command PP-SELECT "PPName1 SOIC" "PPName2 LQFP"
        """
        args = shlex.split(arg)
        if len(args) < 1:
            print("Invalid arguments")
            print(
                "Usage: send_remote_command <rcmd> <cpname1> <cpval1> [<cpname2> <cpval2> ...]")
            return

        rcmd = args[0]
        cp_pairs = []

        if len(args) > 1:
            for i in range(1, len(args), 2):
                if i + 1 < len(args):
                    cpname = args[i]
                    cpval = args[i + 1]
                    cp_pairs.append({"CPNAME": cpname, "CPVAL": cpval})
                else:
                    print("Invalid arguments: cpname without cpval")
                    return

        print(self.gem_host.secs_control.send_remote_command(rcmd, cp_pairs))

    def do_send_enhanched_remote_command(self, arg: str):
        """
        Send enhanced remote command
        Usage: send_enhanched_remote_command <objspec> <rcmd> <cpname1> <cepval1> [<cpname2> <cepval2> ...]
        Sample: send_enhanched_remote_command OBJ-1 PP-SELECT PPName1 SOIC PPName2 LQFP
        """
        args = shlex.split(arg)
        if len(args) < 3:
            print("Invalid arguments")
            print(
                "Usage: send_enhanched_remote_command <objspec> <rcmd> <cpname1> <cepval1> [<cpname2> <cepval2> ...]")
            return

        objspec = args[0]
        rcmd = args[1]
        cp_pairs = []

        if len(args) > 2:
            for i in range(2, len(args), 2):
                if i + 1 < len(args):
                    cpname = args[i]
                    cepval = args[i + 1]
                    cp_pairs.append({"CPNAME": cpname, "CEPVAL": cepval})
                else:
                    print("Invalid arguments: cpname without cepval")
                    return

        # result = self.send_enhanched_remote_command(objspec, rcmd, cp_pairs)
        result = self.gem_host.secs_control.send_enhanched_remote_command(
            objspec, rcmd, cp_pairs)
        print(result)

    # alarm management
    def do_alarms_list(self, arg: str):
        """
        List alarms S7F5
        Usage: alarms_list <alarm_id>
        Sample: alarms_list 1,2,3 or alarms_list
        """
        # alarm_id as list can be empty
        alarm_ids = [int(a) for a in arg.split(",")] if arg else []
        print(self.gem_host.secs_control.alarms_list(alarm_ids))

    def do_alarms_enable_list(self, _):
        """
        List enable alarms S7F7
        Usage: alarms_enable_list
        """
        print(self.gem_host.secs_control.alarms_enable_list())
