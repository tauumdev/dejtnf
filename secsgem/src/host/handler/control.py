from cmd import Cmd
import json
import logging
import os
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.secs.data_items import ACKC7
from typing import TYPE_CHECKING

from config.status_variable_define import CONTROL_STATE_VID, PROCESS_STATE_CHANG_EVENT, SUBSCRIBE_LOT_CONTROL, VID_PP_NAME
from config.app_config import RECIPE_DIR

if TYPE_CHECKING:
    # from src.mqtt.mqtt_client import MqttClient
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

        self.unsubscribe_event_report()
        self.subscribe_lot_control()

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
        response = self.select_equipment_status_request([vid]).get()

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
            s1f4)

        if not isinstance(response, str):
            response = response.get()
            state_name = state.get(response[0], "Unknown")
            self.gem_host.control_state = state_name
            self.gem_host.mqtt_client.client.publish(
                f"equipments/status/control_state/{self.gem_host.equipment_name}", self.gem_host.control_state)
            return state_name

        return response

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
        return response

    def get_equipment_status(self):
        """
        Get equipment status
        """
        # print(getattr(self.gem_host.settings, "connect_mode", None).name)
        status = {
            "equipment_name": self.gem_host.equipment_name,
            "equipment_model": self.gem_host.equipment_model,
            "address": getattr(self.gem_host.settings, "address", None),
            "port": getattr(self.gem_host.settings, "port", None),
            "session_id": self.gem_host.settings.session_id,
            "connect_mode": getattr(self.gem_host.settings, "connect_mode", None).name,
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

        print("Unsubscribe event report : ", self.gem_host.equipment_name)
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

        print("Subscribe lot control : ", self.gem_host.equipment_name)
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

    def reject_lot(self, lot_id: str):
        """
        Reject lot
        """
        if lot_id:
            secs_cmd = {"RCMD": "LOT_REJECT", "PARAMS": [
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

    def add_lot_fclx(self, lot_id: str):
        """
        Open lot
        """
        if lot_id:
            secs_cmd = {"DATAID": 0, "OBJSPEC": "OBJ", "RCMD": "ADD_LOT", "PARAMS": [
                {"CPNAME": "LotID", "CEPVAL": lot_id}]}
            s2f50 = self.gem_host.send_and_waitfor_response(
                self.gem_host.stream_function(2, 49)(secs_cmd))

            if isinstance(s2f50, secsgem.common.Message):
                s2f50_decode = self.gem_host.settings.streams_functions.decode(
                    s2f50)

                hcack = {0: "OK", 1: "Invalid Command", 2: "Cannot Do Now", 3: "Parameter Error",
                         4: "Initiated for Asynchronous Completion", 5: "Rejected, Already in Desired Condition", 6: "Invalid Object"}
                return (f"HCACK: {hcack.get(s2f50_decode.HCACK.get(), 'Unknown code')}")
        return "Lot ID is empty"

    def reject_lot_fclx(self, lot_id: str, reject_reason: str):
        """
        Close lot
        """
        if lot_id:
            secs_cmd = {"DATAID": 101, "OBJSPEC": "LOTCONTROL", "RCMD": "REJECT_LOT",
                        "PARAMS": [
                            {"CPNAME": "LotID", "CEPVAL": lot_id},
                            {"CPNAME": "Reason", "CEPVAL": reject_reason}
                        ]}
            s2f50 = self.gem_host.send_and_waitfor_response(
                self.gem_host.stream_function(2, 49)(secs_cmd))

            if isinstance(s2f50, secsgem.common.Message):
                s2f50_decode = self.gem_host.settings.streams_functions.decode(
                    s2f50)

                hcack = {0: "OK", 1: "Invalid Command", 2: "Cannot Do Now", 3: "Parameter Error",
                         4: "Initiated for Asynchronous Completion", 5: "Rejected, Already in Desired Condition", 6: "Invalid Object"}
                return (f"HCACK: {hcack.get(s2f50_decode.HCACK.get(), 'Unknown code')}")
        return "Lot ID is empty"

    # recipe management
    def _store_recipe(self, recipe_name: str, recipe_data: bytes):
        """
        Store recipe to file
        path: /recipes/equipment_name/uploaded/recipe_name
        """

        # Define base directory
        base_path = os.path.join(
            RECIPE_DIR, self.gem_host.equipment_model, self.gem_host.equipment_name, "upload")

        try:
            os.makedirs(base_path, exist_ok=True)
            # Sanitize filename to prevent path traversal
            safe_file_name = os.path.basename(recipe_name)
            full_path = os.path.join(base_path, safe_file_name)

            # Write recipe data to file
            with open(full_path, "wb") as f:
                f.write(recipe_data)
                print(f"Recipe {recipe_name} stored successfully")
                return True
        except Exception as e:
            print(f"Error storing recipe {recipe_name}: {e}")
            return False

    def _get_recipe(self, recipe_name: str):
        """
        Get recipe from file
        """

        # Define base directory
        base_path = os.path.join(
            RECIPE_DIR, self.gem_host.equipment_model, self.gem_host.equipment_name, "current")

        try:
            # Sanitize filename to prevent path traversal
            safe_file_name = os.path.basename(recipe_name)
            full_path = os.path.join(base_path, safe_file_name)

            # Read recipe data from file
            with open(full_path, "rb") as f:
                recipe_data = f.read()
                print(f"Recipe {recipe_name} read successfully")
                return recipe_data
        except Exception as e:
            print(f"Error reading recipe {recipe_name}: {e}")
            return None

    def pp_list(self):
        """
        S7F19R	Current Process Program Dir Request
        """
        if not self.gem_host.is_online:
            logger.warning("PP Directory Request Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(7, 19)()
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            return self.gem_host.settings.streams_functions.decode(
                response)
        return "No response"

    def pp_load_inquire(self, ppid: str):
        """
        S7F1R	Process Program Load Inquire
        """
        if not self.gem_host.is_online:
            logger.warning("PP Load Inquire Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        pp_body = self._get_recipe(ppid)
        if pp_body is None:
            return f"Recipe {ppid} not found"

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(7, 1)(
                {"PPID": ppid, "LENGTH": len(pp_body)})
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            return self.gem_host.settings.streams_functions.decode(
                response)
        return "No response"

    def pp_load_grant(self, handler: secsgem.secs.SecsHandler, message: secsgem.common.Message):
        """
        S7F2	Process Program Load Grant
        eac =   0 - ok
                1 - one or more constants does not exist
                2 - busy
                3 - one or more values out of range
        """

        self.gem_host.send_response(self.gem_host.stream_function(
            7, 2)(ACKC7.ACCEPTED), message.header.system)

        decode = self.gem_host.settings.streams_functions.decode(message)
        print(decode)
        print(decode.get())

    def pp_request(self, ppid: str):
        """
        S7F5R	Process Program Request
        """
        if not self.gem_host.is_online:
            logger.warning("PP Request Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(7, 5)(ppid)
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            decode_response = self.gem_host.settings.streams_functions.decode(
                response)
            ppid_ = decode_response.PPID.get()
            ppbody = decode_response.PPBODY.get()
            if not ppid or not ppbody:
                print("PPID or PPBODY is empty")
                return "PPID or PPBODY is empty"

            self._store_recipe(ppid_, ppbody)
        return "No response"

    def pp_recive(self, handler: secsgem.secs.SecsHandler, message: secsgem.common.Message):
        """
        Handle S7F3 Process Program Receive
        """
        handler.send_response(self.gem_host.stream_function(
            7, 4)(ACKC7.ACCEPTED), message.header.system)
        decode = self.gem_host.settings.streams_functions.decode(message)

        ppid = decode.PPID.get()
        ppbody = decode.PPBODY.get()
        logger.info("Receive PPID: %s, PPBODY: %s from: %s",
                    ppid, ppbody, self.gem_host.equipment_name)
        if not ppid or not ppbody:
            logger.warning("PPID or PPBODY is empty")
            return

        self._store_recipe(ppid, ppbody)

    def pp_delete(self,  ppids: list[int | str]):
        """
        S7F17	Process Program Delete
        :param ppids: list of PPID to delete
        """
        if not self.gem_host.is_online:
            logger.warning("PP Delete Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(7, 17)(ppids)
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            ackc7 = {0: "Accepted", 1: "Permission not granted", 2: "Length error",
                     3: "Matrix overflow", 4: "PPID not found", 5: "Unsupported mode",
                     6: "Initiated for asynchronous completion", 7: "Storage limit error"}

            response_code = self.gem_host.settings.streams_functions.decode(
                response).get()
            logger.info("PP Delete PPID: %s on %s", ppids,
                        self.gem_host.equipment_name)
            logger.info("PP Delete HCACK: %s",
                        ackc7.get(response_code, f"Unknown code: {response_code}"))
            return ackc7.get(response_code, f"Unknown code: {response_code}")
        logger.warning("PP Delete No response")
        return "No response"

    def pp_send(self, ppid: str):
        """
        S7F3R	Process Program Send
        """
        if not self.gem_host.is_online:
            logger.warning("PP Send Equipment %s is not online",
                           self.gem_host.equipment_name)
            print("Equipment is not online")
            return "Equipment is not online"

        pp_body = self._get_recipe(ppid)
        if pp_body is None:
            return f"Recipe {ppid} not found"
        pp_body_bytes = secsgem.secs.variables.Binary(pp_body)
        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(7, 3)(
                {"PPID": ppid, "PPBODY": pp_body_bytes})
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            ackc7 = {0: "Accepted", 1: "Permission not granted", 2: "Length error",
                     3: "Matrix overflow", 4: "PPID not found", 5: "Unsupported mode",
                     6: "Initiated for asynchronous completion", 7: "Storage limit error"}
            response_code = self.gem_host.settings.streams_functions.decode(
                response).get()
            logger.info("PP Send PPID: %s to %s", ppid,
                        self.gem_host.equipment_name)
            logger.info("PP Send HCACK: %s",
                        ackc7.get(response_code, f"Unknown code: {response_code}"))
            return ackc7.get(response_code, f"Unknown code: {response_code}")
        logger.warning("PP Send No response")
        return "No response"

    def pp_select(self, ppid: str):
        """
        Process Program Select
        :param ppid: Process Program ID
        """
        if not self.gem_host.is_online:
            logger.warning("PP Select Equipment %s is not online",
                           self.gem_host.equipment_name)
            return "Equipment is not online"

        rcmd = {"RCMD": "PP-SELECT", "PARAMS": [
            {"CPNAME": "PPName", "CPVAL": ppid}]}

        response = self.gem_host.send_and_waitfor_response(
            self.gem_host.stream_function(2, 41)(rcmd)
        )
        if isinstance(response, secsgem.hsms.HsmsMessage):
            s2f42_decode = self.gem_host.settings.streams_functions.decode(
                response)
            hcack = {0: "OK", 1: "Invalid Command", 2: "Cannot Do Now", 3: "Parameter Error",
                     4: "Initiated for Asynchronous Completion", 5: "Rejected, Already in Desired Condition", 6: "Invalid Object"}
            logger.info("PP Select PPID: %s on %s", ppid,
                        self.gem_host.equipment_name)
            logger.info("PP Select HCACK: %s", hcack.get(
                s2f42_decode.HCACK.get(), "Unknown code"))
            return (f"HCACK: {hcack.get(s2f42_decode.HCACK.get(), 'Unknown code')}")
        logger.warning("PP Select No response")
        return "No response"

    # # remote command

    def send_remote_command(self, rcmd: str, params: list[str]):
        """
        Send remote command
        :param rcmd: Remote command
        :param params: list of command parameters
        """
        if rcmd:
            secs_cmd = {"RCMD": rcmd, "PARAMS": params}
            print(secs_cmd)
            s2f42 = self.gem_host.send_and_waitfor_response(
                self.gem_host.stream_function(2, 41)(secs_cmd))

            if isinstance(s2f42, secsgem.common.Message):
                s2f42_decode = self.gem_host.settings.streams_functions.decode(
                    s2f42)

                hcack = {0: "OK", 1: "Invalid Command", 2: "Cannot Do Now", 3: "Parameter Error",
                         4: "Initiated for Asynchronous Completion", 5: "Rejected, Already in Desired Condition", 6: "Invalid Object"}
                logger.info("Send RCMD: %s to %s", rcmd,
                            self.gem_host.equipment_name)
                logger.info("RCMD HCACK: %s",
                            hcack.get(s2f42_decode.HCACK.get(), "Unknown code"))
                return (f"HCACK: {hcack.get(s2f42_decode.HCACK.get(), 'Unknown code')}")
        logger.warning("No response")
        return "No response"

    def send_enhanched_remote_command(self, objspec: str, rcmd: str, params: list[str]):
        """
        Send remote command
        :param rcmd: Remote command
        :param params: list of command parameters
        """
        if rcmd:
            # secs_cmd = {"RCMD": rcmd, "PARAMS": params}
            secs_cmd = {"DATAID": 0, "OBJSPEC": objspec, "RCMD": rcmd,
                        "PARAMS": params}
            print(secs_cmd)
            s2f50 = self.gem_host.send_and_waitfor_response(
                self.gem_host.stream_function(2, 49)(secs_cmd))

            if isinstance(s2f50, secsgem.common.Message):
                s2f50_decode = self.gem_host.settings.streams_functions.decode(
                    s2f50)

                hcack = {0: "OK", 1: "Invalid Command", 2: "Cannot Do Now", 3: "Parameter Error",
                         4: "Initiated for Asynchronous Completion", 5: "Rejected, Already in Desired Condition", 6: "Invalid Object"}
                logger.info("Send RCMD: %s to %s", rcmd,
                            self.gem_host.equipment_name)
                logger.info("RCMD HCACK: %s",
                            hcack.get(s2f50_decode.HCACK.get(), "Unknown code"))
                return (f"HCACK: {hcack.get(s2f50_decode.HCACK.get(), 'Unknown code')}")
        logger.warning("No response")
        return "No response"
