import logging
import os
import zipfile
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.hsms.packets import HsmsPacket
from secsgem.secs.dataitems import ACKC7

from typing import TYPE_CHECKING

import secsgem.secs.dataitems

if TYPE_CHECKING:
    from src.gemhost.equipment import Equipment

from src.utils.config.app_config import RECIPE_DIR
from src.utils.config.secsgem_subscribe import PROCESS_STATE_CHANG_EVENT, SUBSCRIBE_LOT_CONTROL, VID_MODEL, VID_CONTROL_STATE, VID_PP_NAME

logger = logging.getLogger("app_logger")


class SecsControl:
    """
    Class for handling SECS control
    """

    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment
        self.recipe_management = self._RecipeManagement(self.equipment)
        self.lot_management = self._LotManagement(self.equipment)
        self.response_message = self.ResponseMessage()

    class ResponseMessage:
        """
        Class for get messages from response code
        """

        def response_message_rcmd(self, code: int):
            """
            Response message S2F42
            0 - ok, completed
            1 - invalid command
            2 - cannot do now
            3 - parameter error
            4 - initiated for asynchronous completion
            5 - rejected, already in desired condition
            6 - invalid object
            """

            message = {0: "OK", 1: "Invalid command", 2: "Cannot do now",
                       3: "Parameter error", 4: "Initiated for asynchronous completion",
                       5: "Rejected, already in desired condition", 6: "Invalid object"}
            return message.get(code, "Unknown code")

        def response_message_onlack(self, code: int):
            """
            Response message Online S1F16
            0 - ok
            1 - refused
            2 - already online
            """

            message = {0: "OK", 1: "Refused", 2: "Already online"}
            return message.get(code, "Unknown code")

        def response_message_oflack(self, code: int):
            """
            Response message Offline S1F18
            0 - ok
            """

            message = {0: "OK"}
            return message.get(code, "Unknown code")

        def response_message_lrack(self, code: int):
            """
            Response message S2F36
            0 - ok
            1 - out of space
            2 - invalid format
            3 - 1 or more CEID links already defined
            4 - 1 or more CEID invalid
            5 - 1 or more RPTID invalid
            """

            message = {0: "OK", 1: "Out of space", 2: "Invalid format",
                       3: "1 or more CEID links already defined", 4: "1 or more CEID invalid",
                       5: "1 or more RPTID invalid"}
            return message.get(code, "Unknown code")

        def response_message_drack(self, code: int):
            """
            Response message S2F34
            0 - ok
            1 - out of space
            2 - invalid format
            3 - 1 or more RPTID already defined
            4 - 1 or more invalid VID
            """

            message = {0: "OK", 1: "Out of space", 2: "Invalid format",
                       3: "1 or more RPTID already defined", 4: "1 or more invalid VID"}
            return message.get(code, "Unknown code")

        def response_message_erack(self, code: int):
            """
            Response message S2F38
            0 - ok
            1 - denied
            """

            message = {0: "OK", 1: "Denied"}
            return message.get(code, "Unknown code")

    class _LotManagement:

        def __init__(self, equipment: "Equipment"):
            self.equipment = equipment

        def accept_lot_fcl(self, lot_id: str):
            """
            accept lot
            """

            if not self.equipment.is_online:
                logger.error("Equipment is not online: %s",
                             self.equipment.equipment_name)
                return {"status": False, "message": "Equipment is not online"}
            if not self.equipment.equipment_model == "FCL":
                logger.error("Invalid equipment model: %s",
                             self.equipment.equipment_model)
                return {"status": False, "message": "Invalid equipment model"}

            secs_cmd = {"RCMD": "LOT_ACCEPT", "PARAMS": [
                {"CPNAME": "LotID", "CPVAL": lot_id}]}
            s2f42 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 41)(secs_cmd))
            decode_s2f42 = self.equipment.secs_decode(s2f42)
            response_code = decode_s2f42.HCACK.get()

            response_message = self.equipment.secs_control.response_message.response_message_rcmd(
                response_code)
            if not response_code == 0:
                logger.error("Accept lot: %s on %s, Error: %s", lot_id,
                             self.equipment.equipment_name, response_message)
                return {"status": False, "message": response_message}
            logger.info("Accept lot: %s on %s", lot_id,
                        self.equipment.equipment_name)
            return {"status": True, "message": "Accept lot success"}

        def reject_lot_fcl(self, lot_id: str):
            """
            reject lot
            """
            if not self.equipment.is_online:
                logger.error("Equipment is not online: %s",
                             self.equipment.equipment_name)
                return {"status": False, "message": "Equipment is not online"}

            if not self.equipment.equipment_model == "FCL":
                logger.error("Invalid equipment model: %s",
                             self.equipment.equipment_model)
                return {"status": False, "message": "Invalid equipment model"}

            secs_cmd = {"RCMD": "LOT_REJECT", "PARAMS": [
                {"CPNAME": "LotID", "CPVAL": lot_id}]}
            s2f42 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 41)(secs_cmd))
            decode_s2f42 = self.equipment.secs_decode(s2f42)
            response_code = decode_s2f42.HCACK.get()

            response_message = self.equipment.secs_control.response_message.response_message_rcmd(
                response_code)
            if not response_code == 0:
                logger.error("Reject lot: %s on %s, Error: %s", lot_id,
                             self.equipment.equipment_name, response_message)
                return {"status": False, "message": response_message}
            logger.info("Reject lot: %s on %s", lot_id,
                        self.equipment.equipment_name)
            return {"status": True, "message": "Reject lot success"}

        def add_lot_fclx(self, lot_id: str):
            """
            add lot fclx
            """
            if not self.equipment.is_online:
                logger.error("Equipment is not online: %s",
                             self.equipment.equipment_name)
                return {"status": False, "message": "Equipment is not online"}

            if not self.equipment.equipment_model == "FCLX":
                logger.error("Invalid equipment model: %s",
                             self.equipment.equipment_model)
                return {"status": False, "message": "Invalid equipment model"}

            s2f49 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 49)({"DATAID": 123, "OBJSPEC": "OBJ", "RCMD": "ADD_LOT", "PARAMS": [{"CPNAME": "LotID", "CPVAL": lot_id}]}))
            response_code = self.equipment.secs_decode(s2f49).HCACK.get()

            response_message = self.equipment.secs_control.response_message.response_message_rcmd(
                response_code)
            if not response_code == 0:
                logger.error("Add lot: %s on %s, Error: %s", lot_id,
                             self.equipment.equipment_name, response_message)
                return {"status": False, "message": response_message}
            logger.info("Add lot: %s on %s", lot_id,
                        self.equipment.equipment_name)
            return {"status": True, "message": "Add lot success"}

        def reject_lot_fclx(self, lot_id: str, reason: str):
            """
            reject lot fclx
            """
            if not self.equipment.is_online:
                logger.error("Equipment is not online: %s",
                             self.equipment.equipment_name)
                return {"status": False, "message": "Equipment is not online"}

            if not self.equipment.equipment_model == "FCLX":
                logger.error("Invalid equipment model: %s",
                             self.equipment.equipment_model)
                return {"status": False, "message": "Invalid equipment model"}

            s2f49 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 49)(
                    {"DATAID": 101, "OBJSPEC": "LOTCONTROL", "RCMD": "REJECT_LOT",
                     "PARAMS": [
                         {"CPNAME": "LotID", "CPVAL": lot_id},
                         {"CPNAME": "Reason", "CPVAL": reason}
                     ]}))
            response_code = self.equipment.secs_decode(s2f49).HCACK.get()

            response_message = self.equipment.secs_control.response_message.response_message_rcmd(
                response_code)
            if not response_code == 0:
                logger.error("Reject lot: %s on %s, Error: %s", lot_id,
                             self.equipment.equipment_name, response_message)
                return {"status": False, "message": response_message}
            logger.info("Reject lot: %s on %s", lot_id,
                        self.equipment.equipment_name)
            return {"status": True, "message": "Reject lot success"}

    class _RecipeManagement:
        def __init__(self, equipment: "Equipment"):
            self.equipment = equipment

        def save_recipe(self, file_name: str, content: bytes):
            """
            Save recipe to a file with error handling.
            Returns True if successful, False otherwise.
            """
            # Define base directory
            base_path = os.path.join(
                RECIPE_DIR, self.equipment.equipment_model, self.equipment.equipment_name, "upload")

            try:
                # Create directory if it doesn't exist
                os.makedirs(base_path, exist_ok=True)

                # Sanitize filename to prevent path traversal
                safe_file_name = os.path.basename(file_name)
                full_path = os.path.join(base_path, safe_file_name)

                # Write content to file
                with open(full_path, 'wb') as file:
                    file.write(content)

                logger.info("File saved successfully: %s", full_path)
                return True

            except IOError as e:
                logger.error("File save error: %s | %s", full_path, str(e))
                return False
            except Exception as e:
                logger.error(
                    "Unexpected error saving file: %s | %s", full_path, str(e))
                return False

        def get_recipe_file(self, file_name: str):
            """
            Get recipe file as content.
            """
            # Define base directory
            base_path = os.path.join(
                RECIPE_DIR, self.equipment.equipment_model, self.equipment.equipment_name, "current", file_name)

            try:
                with open(base_path, "rb") as file:
                    return file.read()
            except Exception as e:
                logger.error("Error reading recipe file: %s", e)
                return None

        def req_load_query(self, ppid: str):
            """
            s7f1
            """
            if not self.equipment.is_online:
                logger.error("Equipment is not online: %s",
                             self.equipment.equipment_name)
                return {"status": False, "message": "Equipment is not online"}

            try:
                s7f2 = self.equipment.send_and_waitfor_response(
                    self.equipment.stream_function(7, 1)({"PPID": ppid, "LENGTH": 0}))
                decode_s7f2 = self.equipment.secs_decode(s7f2)
                logger.info("<<-- S7F2")
                logger.info(decode_s7f2)
                return {"status": True, "message": "Request recipe success"}

            except Exception as e:
                logger.error("Error request recipe: %s", e)
                return {"status": False, "message": "Error request recipe"}

        def receive_load_query(self, handle, packet: HsmsPacket):
            """
            Handle S7F2 Process Program Load Inquire
            """
            logger.info("<<-- S7F2")
            self.equipment.send_response(self.equipment.stream_function(7, 2)(
                ACKC7.ACCEPTED), packet.header.system)
            decode = self.equipment.secs_decode(packet)

            print(decode)

        def pp_dir(self):
            """
            s7f19
            """
            if not self.equipment.is_online:
                logger.error("Equipment is not online: %s",
                             self.equipment.equipment_name)
                return {"status": False, "message": "Equipment is not online"}

            return self.equipment.get_process_program_list()

        def pp_request(self, ppid: str):
            """
            s7f5
            """
            if not self.equipment.is_online:
                logger.error("Equipment is not online: %s",
                             self.equipment.equipment_name)
                return {"status": False, "message": "Equipment is not online"}

            s7f6 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(7, 5)(ppid))
            decode_s7f6 = self.equipment.secs_decode(s7f6)
            ppid = decode_s7f6.PPID.get()
            ppbody = decode_s7f6.PPBODY.get()

            if not ppid or not ppbody:
                logger.error("Request recipe: %s on %s, Error: %s",
                             ppid, self.equipment.equipment_name, "Recipe not found")
                return {"status": False, "message": "Recipe not found"}

            save_recipe = self.equipment.secs_control.recipe_management.save_recipe(
                ppid, ppbody)
            if not save_recipe:
                return {"status": False, "message": "Error saving recipe "}
            return {"status": True, "message": "Request recipe success on upload"}

        def recipe_upload(self, handler, packet: HsmsPacket):
            """
            Receive a recipe from equipment and save it as a ZIP file.
            """
            # Send acknowledgment response
            self.equipment.send_response(self.equipment.stream_function(7, 4)(
                ACKC7.ACCEPTED), packet.header.system)

            # Decode the received packet
            decode = self.equipment.secs_decode(packet)
            ppid = decode.PPID.get()
            ppbody = decode.PPBODY.get()

            if not ppid or not ppbody:
                logger.error("Receive recipe: %s on %s, Error: Recipe not found",
                             ppid, self.equipment.equipment_name)

            self.equipment.secs_control.recipe_management.save_recipe(
                ppid, ppbody)

        def pp_send(self, ppid: str):
            """
            s7f3 - Send a recipe (PPID) to the equipment.
            """
            if not self.equipment.is_online:
                logger.error("Equipment is not online: %s",
                             self.equipment.equipment_name)
                return {"status": False, "message": "Equipment is not online"}

            pp_body = self.get_recipe_file(ppid)
            if not pp_body:
                logger.error("Send recipe: %s on %s, Error: %s",
                             ppid, self.equipment.equipment_name, "Recipe not found")
                return {"status": False, "message": "Recipe not found"}
            pp_body_bytes = secsgem.secs.dataitems.SecsVarBinary(pp_body)
            return self.equipment.send_process_program(ppid=ppid, ppbody=pp_body_bytes)

        def pp_delete(self, ppid: str):
            """
            s7f17
            """
            if not self.equipment.is_online:
                logger.error("Equipment is not online: %s",
                             self.equipment.equipment_name)
                return {"status": False, "message": "Equipment is not online"}
            return self.equipment.delete_process_programs(ppids=[ppid])

        def pp_select(self, ppid: str):
            """
            select process program on exist in equipment
            ppid: process program id
            """

            if not self.equipment.is_online:
                logger.error("Equipment is not online: %s",
                             self.equipment.equipment_name)
                return {"status": False, "message": "Equipment is not online"}

            secs_cmd = {"RCMD": "PP-SELECT", "PARAMS": [
                {"CPNAME": "PPName", "CPVAL": ppid}]}
            s2f42 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 41)(secs_cmd))
            response_code = self.equipment.secs_decode(s2f42).HCACK.get()
            response_message = self.equipment.secs_control.response_message.response_message_rcmd(
                response_code)
            if response_code == 0:
                logger.info("Select PP: %s on %s", ppid,
                            self.equipment.equipment_name)
                return {"status": True, "message": f"Select recipe: {ppid}"}
            else:
                logger.error("Select PP: %s on %s, Error: %s", ppid,
                             self.equipment.equipment_name, response_message)
                return {"status": False, "message": response_message}

    # communication

    def get_control_state(self):
        """
        get control state
        """
        define_state_message = {
            1: "Off-Line/Equipment Off-Line",
            2: "Off-Line/Attempt On-Line",
            3: "Off-Line/Host Off-Line",
            4: "On-Line/Local",
            5: "On-Line/Remote"
        }

        model_vid = VID_CONTROL_STATE

        vid = model_vid.get(self.equipment.equipment_model)
        if not vid:
            logger.warning("Invalid equipment model: %s",
                           self.equipment.equipment_model)
            return "Off-line"
        if not self.equipment.is_enabled:
            return "Off-line"
        try:
            s1f4 = self.equipment.secs_decode(self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 3)([vid]))).get()
            if isinstance(s1f4, list):
                state = define_state_message.get(s1f4[0])
                self.equipment.control_state = state
                return state
            logger.error("Error get control state: %s", s1f4)
            return "Off-line"
        except Exception as e:
            logger.error("Error get control state: %s", e)
            return "Off-line"

    def get_process_state(self):
        """
        get process state
        """
        model_process_state = PROCESS_STATE_CHANG_EVENT.get(
            self.equipment.equipment_model)

        if not model_process_state:
            logger.warning("Get process state: Invalid equipment model: %s",
                           self.equipment.equipment_model)
            return {"status": False, "message": "Get Process State: Invalid equipment model"}
        if not self.equipment.is_online:
            logger.error("Get process state: Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Get Process State: Equipment is not online"}

        if model_process_state:
            vid = model_process_state.get("VID")
            state = model_process_state.get("STATE")
            status = self.equipment.secs_control.req_equipment_status([
                                                                      vid]).get()

            state_code = status[0]
            state_name = next(
                (state_dict[state_code]
                 for state_dict in state if state_code in state_dict),
                # Default if code not found
                f"Unknown State ({state_code})"
            )
            self.equipment.process_state = state_name
            self.equipment.mqtt_client.client.publish(
                f"equipments/status/process_state/{self.equipment.equipment_name}", state_name, 0, retain=True)

            return {"status": True, "message": state_name}

    def get_ppid(self):
        """
        get active recipe
        """
        model_vid = VID_PP_NAME

        vid = model_vid.get(self.equipment.equipment_model)
        if not vid:
            logger.warning("Invalid equipment model: %s",
                           self.equipment.equipment_model)
            return None
        if not self.equipment.is_enabled:
            return None
        try:
            s1f4 = self.equipment.secs_decode(self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 3)([vid]))).get()
            if isinstance(s1f4, list):
                recipe_name = s1f4[0]
                self.equipment.process_program = recipe_name
                return recipe_name
            return None
        except Exception as e:
            logger.error("Error get recipe: %s", e)
            return None

    def get_mdln(self):
        """
        get equipment model
        """
        model_vid = VID_MODEL
        vid = model_vid.get(self.equipment.equipment_model)
        if not vid:
            logger.warning("Invalid equipment model: %s",
                           self.equipment.equipment_model)
            return None
        if not self.equipment.is_enabled:
            return None
        try:
            s1f4 = self.equipment.secs_decode(self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 3)([vid]))).get()
            if isinstance(s1f4, list):
                recipe_name = s1f4[0]
                return recipe_name
            return None
        except Exception as e:
            logger.error("Error get model: %s", e)
            return None

    def enable(self):
        """
        Enable equipment
        """
        if self.equipment.is_enabled:
            return {"status": True, "message": "Equipment is already enabled"}
        self.equipment.is_enabled = True

        return self.equipment.enable()

    def disable(self):
        """
        Disable equipment
        """
        if not self.equipment.is_enabled:
            return {"status": True, "message": "Equipment is already disabled"}
        self.equipment.is_enabled = False
        return self.equipment.disable()

    def online(self):
        """
        Online equipment
        """
        if not self.equipment.is_enabled:
            logger.error("Equipment is not enabled: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not enabled"}
        try:
            response_code = self.equipment.go_online()
            response_message = self.equipment.secs_control.response_message.response_message_onlack(
                response_code)
            if response_code == 0:
                logger.info("Equipment online: %s",
                            self.equipment.equipment_name)
                self.equipment.control_state = "On-Line"
                self.equipment.mqtt_client.client.publish(
                    f"equipments/status/control_state/{self.equipment.equipment_name}", "On-Line", 0, retain=True)
                return {"status": True, "message": "Equipment online"}
            else:
                logger.warning("Equipment online: %s, WARNING: %s",
                               self.equipment.equipment_name, response_message)
                return {"status": False, "message": response_message}
        except Exception as e:
            logger.error("Error online equipment: %s", e)
            return {"status": False, "message": "Error online equipment"}

    def offline(self):
        """
        Offline equipment
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}
        try:
            response_code = self.equipment.go_offline()
            response_message = self.equipment.secs_control.response_message.response_message_oflack(
                response_code)
            if response_code == 0:
                logger.info("Equipment offline: %s",
                            self.equipment.equipment_name)
                self.equipment.control_state = "Off-Line"
                self.equipment.mqtt_client.client.publish(
                    f"equipments/status/control_state/{self.equipment.equipment_name}", "Off-Line", 0, retain=True)
                return {"status": True, "message": "Equipment offline"}
            else:
                logger.warning("Equipment offline: %s, WARNING: %s",
                               self.equipment.equipment_name, response_message)
                return {"status": False, "message": response_message}
        except Exception as e:
            logger.error("Error offline equipment: %s", e)
            return {"status": False, "message": "Error offline equipment"}

    def status(self):
        """
        equipment communication status
        """
        equipment_status = {
            "address": self.equipment.address,
            "port": self.equipment.port,
            "session_id": self.equipment.sessionID,
            "active": self.equipment.active,
            "enabled": self.equipment.is_enabled,
            "communicating": self.equipment.communicationState.current,
            "control_state": self.equipment.control_state,
            "process_state": self.equipment.process_state,
            "process_program": self.equipment.process_program,
            "lot_active": self.equipment.lot_active
        }
        return equipment_status

    # request equipment status

    def req_equipment_status(self, svids: list[int]):
        """
        s1f3
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}

        s1f4 = self.equipment.send_and_waitfor_response(
            self.equipment.stream_function(1, 3)(svids))
        return self.equipment.secs_decode(s1f4)

    def req_equipment_constant(self, ceids: list[int] = None):
        """
        s2f13
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}

        s2f14 = self.equipment.send_and_waitfor_response(
            self.equipment.stream_function(2, 13)(ceids))
        return self.equipment.secs_decode(s2f14)

    def req_status_variable_namelist(self, svids: list[int] = None):
        """
        s1f11
        Comment: Host sends L:0 to request all SVIDs.
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}
        s1f12 = self.equipment.send_and_waitfor_response(
            self.equipment.stream_function(1, 11)(svids))
        return self.equipment.secs_decode(s1f12)

    def req_equipment_constant_namelist(self, ecids: list[int] = None):
        """
        s2f29
        Comment: Host sends L:0 for all ECIDs
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}
        s2f30 = self.equipment.send_and_waitfor_response(
            self.equipment.stream_function(2, 29)(ecids))
        return self.equipment.secs_decode(s2f30)

    def req_s1f21(self, vids: list[int] = None):
        """
        s1f21 Data Variable Namelist Request
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}
        s1f12 = self.equipment.send_and_waitfor_response(
            self.equipment.stream_function(1, 21)(vids))
        return self.equipment.secs_decode(s1f12)

    def req_event_report(self, ceid: int):
        """
        s6f15 event report request
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}
        s6f16 = self.equipment.send_and_waitfor_response(
            self.equipment.stream_function(6, 15)(ceid))
        return self.equipment.secs_decode(s6f16)
    # define equipment events

    def enable_events(self, ceids: list[int] = None):
        """
        s2f37 CEED=True
        Comment: n=0 means all CEIDs
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}
        s2f38 = self.equipment.send_and_waitfor_response(
            self.equipment.stream_function(2, 37)({"CEED": True, "CEID": ceids}))
        return self.equipment.secs_decode(s2f38)

    def disable_events(self, ceids: list[int] = None):
        """
        s2f37 CEED=False
        Comment: n=0 means all CEIDs
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}

        s2f38 = self.equipment.send_and_waitfor_response(
            self.equipment.stream_function(2, 37)({"CEED": False, "CEID": ceids}))
        return self.equipment.secs_decode(s2f38)

    def subscribe_event(self, ceid: int, dvs: list[int], report_id: int = None):
        """
        Subscribe to a collection event.

        :param ceid: ID of the collection event
        :type ceid: integer
        :param dvs: DV IDs to add for collection event
        :type dvs: list of integers
        :param report_id: optional - ID for report, autonumbering if None
        :type report_id: integer
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}
        if report_id is None:
            report_id = self.equipment.reportIDCounter
            self.equipment.reportIDCounter += 1

        # note subscribed reports
        self.equipment.reportSubscriptions[report_id] = dvs

        # create report
        resp_create = self.equipment.send_and_waitfor_response(self.equipment.stream_function(2, 33)(
            {"DATAID": 0, "DATA": [{"RPTID": report_id, "VID": dvs}]}))

        resp_create_code = self.equipment.secs_decode(
            resp_create).get()
        resp_create_message = self.equipment.secs_control.response_message.response_message_drack(
            resp_create_code)
        if resp_create_code != 0:
            return {"status": False, "message": resp_create_message}

        # link event report to collection event
        resp_link = self.equipment.send_and_waitfor_response(self.equipment.stream_function(2, 35)(
            {"DATAID": 0, "DATA": [{"CEID": ceid, "RPTID": [report_id]}]}))
        resp_link_code = self.equipment.secs_decode(
            resp_link).get()

        resp_link_message = self.equipment.secs_control.response_message.response_message_lrack(
            resp_link_code)
        if resp_link_code != 0:
            return {"status": False, "message": resp_link_message}

        # enable collection event
        resp_enable = self.equipment.send_and_waitfor_response(
            self.equipment.stream_function(2, 37)({"CEED": True, "CEID": [ceid]}))
        resp_enable_code = self.equipment.secs_decode(
            resp_enable).get()
        resp_enable_message = self.equipment.secs_control.response_message.response_message_erack(
            resp_enable_code)

        if resp_enable_code != 0:
            return {"status": False, "message": resp_enable_message}
        return {"status": True, "message": "Event subscribed"}

    def unsubscribe_event(self, report_id: int = None):
        """
        s2f33
        Comment: a=0 means delete all reports and event links, b=0 means delete the RPTID type and its event links
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}

        resp_unsubscribe = self.equipment.send_and_waitfor_response(self.equipment.stream_function(2, 33)(
            {"DATAID": 0, "DATA": [{"RPTID": report_id, "VID": []}]}))

        resp_ubsubscribe_code = self.equipment.secs_decode(
            resp_unsubscribe).get()
        resp_unscribe_message = self.equipment.secs_control.response_message.response_message_drack(
            resp_ubsubscribe_code)
        if resp_ubsubscribe_code != 0:
            return {"status": False, "message": resp_unscribe_message}

        return {"status": True, "message": "Event unsubscribed"}

    def unsubscribe_all_events(self):
        """
        Unsubscribe all events
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}

        resp_unsubscribe = self.equipment.send_and_waitfor_response(self.equipment.stream_function(2, 33)(
            {"DATAID": 0, "DATA": []}))

        resp_ubsubscribe_code = self.equipment.secs_decode(
            resp_unsubscribe).get()
        resp_unscribe_message = self.equipment.secs_control.response_message.response_message_drack(
            resp_ubsubscribe_code)
        if resp_ubsubscribe_code != 0:
            return {"status": False, "message": resp_unscribe_message}

        return {"status": True, "message": "Unsubscribed all link event"}

    # def subscribe_lot_control(self):
    #     """
    #     Subscribe lot control event
    #     """
    #     if not self.equipment.is_online:
    #         logger.error("Equipment is not online: %s",
    #                      self.equipment.equipment_name)
    #         return {"status": False, "message": "Equipment is not online"}

    #     model_subscribe = {"FCL": SUBSCRIBE_LOT_CONTROL_FCL,
    #                        "FCLX": SUBSCRIBE_LOT_CONTROL_FCLX}
    #     subscribe = model_subscribe.get(self.equipment.equipment_model)
    #     if not subscribe:
    #         return {"status": False, "message": "Invalid equipment model"}

    #     for sub in subscribe:
    #         ceid = sub.get("ceid")
    #         dvs = sub.get("dvs")
    #         report_id = sub.get("report_id")
    #         self.subscribe_event(ceid, dvs, report_id)
    #     return {"status": True, "message": "Event subscribed"}

    def subscribe_lot_control(self):
        """
        Subscribe lot control event
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}

        # SUBSCRIBE_LOT_CONTROL = {
        #     "FCL": [
        #         # subscribe request validate lot
        #         {"ceid": 20, "dvs": [81, 33], "report_id": 1000},
        #         # subscribe lot open
        #         {"ceid": 21, "dvs": [82, 33], "report_id": 1001},
        #         # subscribe lot close
        #         {"ceid": 22, "dvs": [83, 33], "report_id": 1002},
        #         # subscribe recipe init
        #         # {"ceid": 1, "dvs": [33], "report_id": 1003}
        #     ],
        #     "FCLX": [
        #         # subscribe request validate lot
        #         {"ceid": 58, "dvs": [3081, 7], "report_id": 1000},
        #         # subscribe lot open
        #         {"ceid": 40, "dvs": [3026, 7], "report_id": 1001},
        #         # subscribe lot close
        #         {"ceid": 41, "dvs": [3027, 7], "report_id": 1002},
        #         # subscribe recipe init
        #         # {"ceid": 10, "dvs": [7], "report_id": 1003}
        #     ],
        #     # "STI": [
        #     #     # subscribe request validate lot
        #     #     {"ceid": 101, "dvs": [81, 33], "report_id": 1000},
        #     #     # subscribe lot open
        #     #     {"ceid": 218, "dvs": [82, 33], "report_id": 1001},
        #     #     # subscribe lot close
        #     #     {"ceid": 220, "dvs": [83, 33], "report_id": 1002},
        #     #     # subscribe recipe init
        #     #     # {"ceid": 1, "dvs": [33], "report_id": 1003}
        #     # ]
        # }

        subscribe = SUBSCRIBE_LOT_CONTROL.get(self.equipment.equipment_model)
        if not subscribe:
            logger.error("Subscribe lot control: Invalid equipment model: %s",
                         self.equipment.equipment_model)
            return {"status": False, "message": "Invalid equipment model"}

        for sub in subscribe:
            ceid = sub.get("ceid")
            dvs = sub.get("dvs")
            report_id = sub.get("report_id")
            response = self.subscribe_event(ceid, dvs, report_id)

            if not response.get("status"):
                logger.error("Subscribe lot control: %s on %s, Error: %s",
                             ceid, self.equipment.equipment_name, response.get("message"))
                return response
            logger.info("Subscribe lot control: %s on %s",
                        ceid, self.equipment.equipment_name)
        return {"status": True, "message": "Event subscribed"}

    # sti commands

    def sti_pp_select(self, ppid: str):
        """
        STI PP-SELECT
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}

        cmd = {"RCMD": "PPSELECT", "PARAMS": [
            {"CPNAME": "RecipeName", "CPVAL": ppid}
        ]}

        try:
            s2f42 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 41)(cmd))
            response_code = self.equipment.secs_decode(s2f42).HCACK.get()
            response_message = self.equipment.secs_control.response_message.response_message_rcmd(
                response_code)
            print(response_message)
        except Exception as e:
            print(e)

    def sti_lot_end(self):
        """
        STI LOT-END
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}

        cmd = {
            "RCMD": "LOTEND", "PARAMS": [
            ]
        }
        try:
            s2f42 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 41)(cmd))
            response_code = self.equipment.secs_decode(s2f42).HCACK.get()
            response_message = self.equipment.secs_control.response_message.response_message_rcmd(
                response_code)
            print(response_message)
        except Exception as e:
            print(e)

    def sti_go_local(self):
        """
        STI GO-LOCAL
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}
        cmd = {
            "RCMD": "GOLOCAL", "PARAMS": [
            ]
        }
        try:
            s2f42 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 41)(cmd))
            response_code = self.equipment.secs_decode(s2f42).HCACK.get()
            response_message = self.equipment.secs_control.response_message.response_message_rcmd(
                response_code)
            print(response_message)
        except Exception as e:
            print(e)
