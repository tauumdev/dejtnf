import logging
import os
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.hsms.packets import HsmsPacket
from secsgem.secs.dataitems import ACKC7

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gemhost.equipment import Equipment

from src.utils.config.app_config import RECIPE_DIR
from src.utils.config.secsgem_subscribe import SUBSCRIBE_LOT_CONTROL_FCL, SUBSCRIBE_LOT_CONTROL_FCLX, VID_MODEL, VID_CONTROL_STATE, VID_PP_NAME

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
        Class for response messages
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

            if not self.equipment.equipment_model == "FCL":
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

            if not self.equipment.equipment_model == "FCL":
                logger.error("Invalid equipment model: %s",
                             self.equipment.equipment_model)
                return {"status": False, "message": "Invalid equipment model"}

            s2f49 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 49)({"DATAID": 101, "OBJSPEC": "LOTCONTROL", "RCMD": "REJECT_LOT", "PARAMS": [{"CPNAME": "LotID", "CPVAL": lot_id}, {"CPNAME": "LotID", "CPVAL": reason}]}))
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

        # Check dir path for recipe file if not exist create
        # receipe update = files/recipe/equipment_model/equipment_name/current/recipe_name
        # recipe backup = files/recipe/equipment_model/equipment_name/backup/receipe_name
        # recipe upload = files/recipe/equipment_model/equipment_name/upload/receipe_name

        def create_dir(self, path: str):
            """
            create directory
            """
            try:
                if not os.path.exists(path):
                    os.makedirs(path)
            except Exception as e:
                logger.error("Error creating directory: %s", e)

        def get_recipe_file(self, path: str):
            """
            get recipe file
            return secs binary
            """
            try:
                with open(path, "r", encoding="utf-8") as f:
                    if not f:
                        return None
                    return secsgem.secs.variables.SecsVarBinary(f.read())
            except Exception as e:
                logger.error("Error reading recipe file: %s", e)
                return None

        def pp_dir(self):
            """
            s7f19
            """
            if self.equipment.is_online:
                logger.error("Equipment is not online: %s",
                             self.equipment.equipment_name)
                return {"status": False, "message": "Equipment is not online"}

            return self.equipment.get_process_program_list()

        def pp_request(self, ppid: str):
            """
            s7f5
            """
            if self.equipment.is_online:
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
            try:
                path = os.path.join(
                    RECIPE_DIR, self.equipment.equipment_model,
                    self.equipment.equipment_name, "upload"
                )
                self.create_dir(path)
                with open(f"{path}/{ppid}", "w", encoding="utf-8") as f:
                    f.write(ppbody.decode('utf-8'))
                return {"status": True, "message": "Request recipe success on upload"}
            except Exception as e:
                logger.error("Request recipe: %s on %s, Error: %s",
                             ppid, self.equipment.equipment_name, e)
                return {"status": False, "message": str(e)}

        def receive_recipe(self, handler, packet: HsmsPacket):
            """
            receive recipe frome equipment save to upload path
            """
            self.equipment.send_response(self.equipment.stream_function(7, 4)(
                ACKC7.ACCEPTED), packet.header.system)
            decode = self.equipment.secs_decode(packet)
            ppid = decode.PPID.get()
            ppbody = decode.PPBODY.get()
            if not ppid or not ppbody:
                logger.error("Receive recipe: %s on %s, Error: %s",
                             ppid, self.equipment.equipment_name, "Recipe not found")
            try:
                path = os.path.join(
                    RECIPE_DIR, self.equipment.equipment_model,
                    self.equipment.equipment_name, "upload"
                )
                self.create_dir(path)
                with open(f"{path}/{ppid}", "w", encoding="utf-8") as f:
                    f.write(ppbody.decode('utf-8'))

                logger.info("Receive recipe: %s on %s", ppid,
                            self.equipment.equipment_name)
                # return {"status": True, "message": "Receive recipe success"}
            except Exception as e:
                logger.error("Receive recipe: %s on %s, Error: %s",
                             ppid, self.equipment.equipment_name, e)
                return {"status": False, "message": str(e)}

        def pp_send(self, ppid: str):
            """
            s7f3
            """
            if self.equipment.is_online:
                logger.error("Equipment is not online: %s",
                             self.equipment.equipment_name)
                return {"status": False, "message": "Equipment is not online"}

            path = os.path.join(
                RECIPE_DIR, self.equipment.equipment_model,
                self.equipment.equipment_name, "current", ppid
            )
            pp_body = self.get_recipe_file(path)
            if not pp_body:
                logger.error("Send recipe: %s on %s, Error: %s",
                             ppid, self.equipment.equipment_name, "Recipe not found")
                return {"status": False, "message": "Recipe not found"}
            return self.equipment.send_process_program(ppid=ppid, ppbody=pp_body)

        def pp_delete(self, ppid: str):
            """
            s7f17
            """
            if self.equipment.is_online:
                logger.error("Equipment is not online: %s",
                             self.equipment.equipment_name)
                return {"status": False, "message": "Equipment is not online"}
            return self.equipment.delete_process_programs(ppids=[ppid])

        def pp_select(self, ppid: str):
            """
            select process program on exist in equipment
            ppid: process program id
            """

            if self.equipment.is_online:
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
            return "Off-line"
        except Exception as e:
            logger.error("Error get control state: %s", e)
            return "Off-line"

    def get_ppid(self):
        """
        get active recipe
        """
        model_vid = VID_PP_NAME

        vid = model_vid.get(self.equipment.equipment_model)
        if not vid:
            logger.warning("Invalid equipment model: %s",
                           self.equipment.equipment_model)
            return "Can not get recipe"

        try:
            s1f4 = self.equipment.secs_decode(self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 3)([vid]))).get()
            if isinstance(s1f4, list):
                recipe_name = s1f4[0]
                return recipe_name
            return "Can not get recipe"
        except Exception as e:
            logger.error("Error get recipe: %s", e)
            return "Can not get recipe"

    def get_mdln(self):
        """
        get equipment model
        """
        model_vid = VID_MODEL
        vid = model_vid.get(self.equipment.equipment_model)
        if not vid:
            logger.warning("Invalid equipment model: %s",
                           self.equipment.equipment_model)
            return "Can not get model"
        try:
            s1f4 = self.equipment.secs_decode(self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 3)([vid]))).get()
            if isinstance(s1f4, list):
                recipe_name = s1f4[0]
                return recipe_name
            return "Can not get model"
        except Exception as e:
            logger.error("Error get model: %s", e)
            return "Can not get model"

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
            "ppid": self.equipment.ppid,
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

    def subscribe_lot_control(self):
        """
        Subscribe lot control event
        """
        if not self.equipment.is_online:
            logger.error("Equipment is not online: %s",
                         self.equipment.equipment_name)
            return {"status": False, "message": "Equipment is not online"}

        model_subscribe = {"FCL": SUBSCRIBE_LOT_CONTROL_FCL,
                           "FCLX": SUBSCRIBE_LOT_CONTROL_FCLX}
        subscribe = model_subscribe.get(self.equipment.equipment_model)
        if not subscribe:
            return {"status": False, "message": "Invalid equipment model"}

        for sub in subscribe:
            ceid = sub.get("ceid")
            dvs = sub.get("dvs")
            report_id = sub.get("report_id")
            self.subscribe_event(ceid, dvs, report_id)
        return {"status": True, "message": "Event subscribed"}
