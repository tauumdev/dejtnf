from cmd import Cmd
import json
import logging
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs

from typing import TYPE_CHECKING

from config.status_variable_define import CONTROL_STATE_VID, PROCESS_STATE_CHANG_EVENT, SUBSCRIBE_LOT_CONTROL, VID_PP_NAME

if TYPE_CHECKING:
    from src.mqtt.mqtt_client import MqttClient
    from src.host.gemhost import SecsGemHost

logger = logging.getLogger("app_logger")


class SecsControl(Cmd):
    """
    Class for control SECS/GEM equipment with command line interface
    """

    def __init__(self, gem_host: 'SecsGemHost'):
        super().__init__()
        self.prompt = f"{gem_host.equipment_name}> "
        self.gem_host = gem_host

    def initial_equipment(self):
        """
        Initial equipment
        - Subscribe lot control
        - Get equipment status
        """
        logger.info(
            "Initial equipment Subscribe lot control and Get equipment status")
        print("Initial equipment Subscribe lot control and Get equipment status")

        self.get_control_state()
        self.get_process_state()
        self.get_process_program()

    # communication control
    def enable_equipment(self):
        """
        Enable equipment communication
        """
        if not self.gem_host.is_enable:
            self.gem_host.enable()
            self.gem_host.is_enable = True
            return "Equipment enabled"

        return "Equipment already enabled"

    def disable_equipment(self):
        """
        Disable equipment communication
        """
        if self.gem_host.is_enable:
            self.gem_host.disable()
            self.gem_host.is_enable = False
            return "Equipment disabled"

        return "Equipment already disabled"

    def communication_request(self):
        """
        S1F13 Establish Communications Request
        """
        if not self.gem_host.is_communicating:
            logger.warning("Request Communication Equipment %s is not communicating",
                           self.gem_host.equipment_name)
            print("Equipment is not communicating")
            return "Equipment is not communicating"

        return self.gem_host.settings.streams_functions.decode(
            self.gem_host.send_and_waitfor_response(
                self.gem_host.stream_function(1, 13)()
            )).get()

    def online_request(self):
        """
        S1F17 Establish Online Request
        """
        if not self.gem_host.is_communicating:
            logger.warning("Request Online Equipment %s is not communicating",
                           self.gem_host.equipment_name)
            print("Equipment is not communicating")
            return "Equipment is not communicating"

        onlack = {0: "ok", 1: "refused", 2: "already online"}

        # response = self.gem_host.settings.streams_functions.decode(
        #     self.gem_host.send_and_waitfor_response(
        #         self.gem_host.stream_function(1, 17)()
        #     )).get()

        s1f18 = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(1, 17)()
        )
        if not isinstance(s1f18, secsgem.hsms.HsmsMessage):
            return "No response"
        response = self.gem_host.settings.streams_functions.decode(
            s1f18).get()

        if isinstance(response, int):
            return onlack.get(response, f"unknown code: {response}")
        return "No response"

    def offline_request(self):
        """
        S1F15 Establish Offline Request
        """
        if not self.gem_host.is_communicating:
            logger.warning("Request Offline Equipment %s is not communicating",
                           self.gem_host.equipment_name)
            print("Equipment is not communicating")
            return "Equipment is not communicating"

        offlack = {0: "ok"}

        s1f16 = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(1, 15)()
        )
        if not isinstance(s1f16, secsgem.hsms.HsmsMessage):
            return "No response"
        response = self.gem_host.settings.streams_functions.decode(
            s1f16).get()

        if isinstance(response, int):
            return offlack.get(response, f"unknown code: {response}")
        return "No response"

    def get_process_state(self):
        """
        Get process state
        """
        if not self.gem_host.is_online:
            logger.warning("Get Process State Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        vid_model = PROCESS_STATE_CHANG_EVENT.get(
            self.gem_host.equipment_model)
        if vid_model is None:
            return f"PROCESS_STATE_CHANG_EVENT is not define for {self.gem_host.equipment_model}"

        vid = vid_model.get("VID")
        state = vid_model.get("STATE")
        response = self.select_equipment_status_request([vid])

        if isinstance(response, list):
            state_name = next(state_dict[response[0]]
                              for state_dict in state if response[0] in state_dict)
            self.gem_host.process_state = state_name
            self.gem_host.mqtt_client.client.publish(
                f"equipments/status/process_state/{self.gem_host.equipment_name}", self.gem_host.process_state)
            return state_name
        return "Failed to get process state"

    def get_control_state(self):
        """
        Get control state
        """
        if not self.gem_host.is_communicating:
            logger.warning("Get Control State Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        vid_model = CONTROL_STATE_VID.get(self.gem_host.equipment_model)
        if vid_model is None:
            return f"CONTROL_STATE_VID is not define for {self.gem_host.equipment_model}"
        vid = vid_model.get("VID")
        state = vid_model.get("STATE")

        s1f4 = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(1, 3)([vid])
        )
        if not isinstance(s1f4, secsgem.hsms.HsmsMessage):
            return "Failed to get control state"

        response = self.gem_host.settings.streams_functions.decode(
            s1f4).get()

        if isinstance(response, list):
            state_name = state.get(response[0], "Unknown")
            self.gem_host.control_state = state_name
            self.gem_host.mqtt_client.client.publish(
                f"equipments/status/control_state/{self.gem_host.equipment_name}", self.gem_host.control_state)
            return state_name
        return "Failed to get control state"

    def get_process_program(self):
        """
        Get process program
        """
        if not self.gem_host.is_online:
            logger.warning("Get Process Program Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"
        vid_model = VID_PP_NAME.get(self.gem_host.equipment_model)

        if vid_model is None:
            return f"VID_PP_NAME is not define for {self.gem_host.equipment_model}"

        response = self.select_equipment_status_request([vid_model])
        if not isinstance(response, str):
            response = response.get()
            self.gem_host.process_program = response[0]
            self.gem_host.mqtt_client.client.publish(
                f"equipments/status/process_program/{self.gem_host.equipment_name}", self.gem_host.process_program)
            return response[0]

    def get_equipment_status(self):
        """
        Get equipment status
        """
        status = {
            "equipment_name": self.gem_host.equipment_name,
            "equipment_model": self.gem_host.equipment_model,
            "address": getattr(self.gem_host.settings, "address", None),
            "port": getattr(self.gem_host.settings, "port", None),
            "session_id": self.gem_host.settings.session_id,
            "is_enable": self.gem_host.is_enable,
            "is_communication": self.gem_host.is_communicating,
            "control_state": self.get_control_state(),
            "process_state": self.get_process_state(),
            "process_program": self.get_process_program(),
            "active_lot": self.gem_host.active_lot
        }
        return json.dumps(status, indent=4)

    # get equipment status and variable
    def select_equipment_status_request(self, vids: list[int] = None):
        """
        S1F3 Select Equipment Status Request
        """
        if not self.gem_host.is_online:
            logger.warning("Select Equipment Status Request Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        if vids is None:
            vids = []

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(1, 3)(vids)
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            return self.gem_host.settings.streams_functions.decode(
                response)
        return "No response"

    def status_variable_namelist_request(self, svids: list[int] = None):
        """
        S1F11R	Status Variable Namelist Request
        """
        if not self.gem_host.is_online:
            logger.warning("Status Variable Namelist Request Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        if svids is None:
            svids = []

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(1, 11)(svids)
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            return self.gem_host.settings.streams_functions.decode(
                response)
        return "No response"

    def data_variable_namelist_request(self, vids: list[int] = None):
        """
        S1F21R	Data Variable Namelist Request
        """
        if not self.gem_host.is_online:
            logger.warning("Data Variable Namelist Request Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        if vids is None:
            vids = []

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(1, 21)(vids)
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            return self.gem_host.settings.streams_functions.decode(
                response)
        return "No response"

    def collection_event_namelist_request(self, ceids: list[int] = None):
        """
        S1F23R	Collection Event Namelist Request
        """
        if not self.gem_host.is_online:
            logger.warning("Collection Event Namelist Request Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        if ceids is None:
            ceids = []

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(1, 23)(ceids)
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            return self.gem_host.settings.streams_functions.decode(
                response)
        return "No response"

    def equipment_constant_request(self, ecids: list[int] = None):
        """
        S2F13R	Equipment Constant Request
        """
        if not self.gem_host.is_online:
            logger.warning("Equipment Constant Request Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        if ecids is None:
            ecids = []

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(2, 13)(ecids)
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            return self.gem_host.settings.streams_functions.decode(
                response)
        return "No response"

    def equipment_constant_namelist_request(self, ecids: list[int] = None):
        """
        S2F29R	Equipment Constant Namelist Request
        """
        if not self.gem_host.is_online:
            logger.warning("Equipment Constant Namelist Request Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        if ecids is None:
            ecids = []

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(2, 29)(ecids)
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            return self.gem_host.settings.streams_functions.decode(
                response)
        return "No response"

    # event and report
    def enable_disable_event(self, enable: bool, ceids: list[int] = None):
        """
        2F37 Enable/Disable Event Report
        """
        if not self.gem_host.is_online:
            logger.warning("Enable/Disable Event Report Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        if ceids is None:
            ceids = []

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(2, 37)([int(enable), ceids])
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            erack = {0: "ok", 1: "denied"}
            erack_code = self.gem_host.settings.streams_functions.decode(
                response).get()
            return erack.get(erack_code, f"unknown code: {erack_code}")
        return "No response"

    def define_report(self, vids: list[int], report_id: int):
        """
        S2F33 Define Report
        """
        if not self.gem_host.is_online:
            logger.warning("Define Report Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(2, 33)(
                {"DATAID": 0, "DATA": [{"RPTID": report_id, "VID": vids}]})
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            drack = {0: "ok", 1: "out of space", 2: "invalid format",
                     3: "1 or more RPTID already defined", 4: "1 or more invalid VID"}
            drack_code = self.gem_host.settings.streams_functions.decode(
                response).get()
            return drack.get(drack_code, f"unknown code: {drack_code}")
        return "No response"

    def link_event_report(self, ceid: int, report_id: int):
        """
        2F35 Link Event Report
        """
        if not self.gem_host.is_online:
            logger.warning("Link Event Report Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(2, 35)(
                {"DATAID": 0, "DATA": [{"CEID": ceid, "RPTID": [report_id]}]})
        )

        if isinstance(response, secsgem.hsms.HsmsMessage):
            lrack = {0: "ok", 1: "out of space", 2: "invalid format",
                     3: "1 or more CEID links already defined", 4: "1 or more CEID invalid", 5: "1 or more RPTID invalid"}
            lrack_code = self.gem_host.settings.streams_functions.decode(
                response).get()
            return lrack.get(lrack_code, f"unknown code: {lrack_code}")
        return "No response"

    def subscribe_event_report(self, ceid: int, dvs: list[int], report_id: int):
        """
        Subscribe collection event report
        """
        drack = self.define_report(dvs, report_id)
        if drack != "ok":
            return drack
        lrack = self.link_event_report(ceid, report_id)
        if lrack != "ok":
            return lrack
        erack = self.enable_disable_event(True, [ceid])
        if erack != "ok":
            return erack
        return f"Subscribe CEID {ceid} VIDs {dvs} Report ID {report_id} success"

    def unsubscribe_event_report(self):
        """
        S2F33 Define Report
        """
        if not self.gem_host.is_online:
            logger.warning("Undefine Report Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(2, 33)(
                {"DATAID": 0, "DATA": []})
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            drack = {0: "ok", 1: "out of space", 2: "invalid format",
                     3: "1 or more RPTID already defined", 4: "1 or more invalid VID"}
            drack_code = self.gem_host.settings.streams_functions.decode(
                response).get()
            return drack.get(drack_code, f"unknown code: {drack_code}")
        return "No response"

    def subscribe_lot_control(self):
        """
        Subscribe lot control
        """

        subscribe = SUBSCRIBE_LOT_CONTROL.get(self.gem_host.equipment_model)
        if subscribe is None:
            return f"SUBSCRIBE_LOT_CONTROL is not define for {self.gem_host.equipment_model}"

        for sub in subscribe:
            ceid = sub.get("CEID")
            dvs = sub.get("DVS")
            report_id = sub.get("REPORT_ID")
            if ceid is None or dvs is None or report_id is None:
                return "CEID or DVS or Report ID is not define"
            print(self.subscribe_event_report(ceid, dvs, report_id))

    # lot management
    def accept_lot(self, lot_id: str):
        """
        Accept lot
        """
        if lot_id:
            secs_cmd = {"RCMD": "LOT_ACCEPT", "PARAMS": [
                {"CPNAME": "LotID", "CPVAL": lot_id}]}

            s2f42 = self.gem_host.send_and_waitfor_response(
                self.gem_host.stream_function(2, 41)(secs_cmd))

            if isinstance(s2f42, secsgem.common.Message):
                s2f42_decode = self.gem_host.settings.streams_functions.decode(
                    s2f42)

                hcack = {0: "OK", 1: "Invalid Command", 2: "Cannot Do Now", 3: "Parameter Error",
                         4: "Initiated for Asynchronous Completion", 5: "Rejected, Already in Desired Condition", 6: "Invalid Object"}
                return (f"HCACK: {hcack.get(s2f42_decode.HCACK.get(), 'Unknown code')}")
        return "Lot ID is empty"
