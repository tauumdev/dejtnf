import logging
import os
import threading
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.hsms.packets import HsmsPacket
from secsgem.secs.functionbase import SecsStreamFunction

from secsgem.secs.dataitems import DATAID, ACKC5, ACKC6, ACKC7, RCMD, CPNAME, CPVAL, HCACK, CPACK, OBJSPEC


from src.validate.validate_lot import ValidateLot
from src.utils.logger.gem_logger import CommunicationLogFileHandler

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.mqtt.mqtt_client import MqttClient

from src.utils.config.app_config import RECIPE_DIR

logger = logging.getLogger("app_logger")


class Equipment(secsgem.gem.GemHostHandler):
    """
    Class for handling equipment
    """

    def __init__(self, equipment_name, equipment_model, address, port, session_id, active, enable, mqtt_client_instant: 'MqttClient', custom_connection_handler=None):
        super().__init__(address, port, active, session_id,
                         equipment_name, custom_connection_handler)
        self.mqtt_client = mqtt_client_instant
        self.equipment_name = equipment_name
        self.equipment_model = equipment_model
        self.is_enabled = enable

        self.control_state = None
        self.pp_name = None
        self.lot_active = None

        self.custom_stream_function = self.CustomStreamFunction
        self.secsStreamsFunctions[2].update(
            {49: self.custom_stream_function.SecsS02F49, 50: self.custom_stream_function.SecsS02F50})

        self.register_callbacks = self.CommunicationCallbacks(self)
        self.register_stream_function(1, 14, self.register_callbacks.s01f14)
        self.register_stream_function(9, 1, self.register_callbacks.s09f1)
        self.register_stream_function(9, 3, self.register_callbacks.s09f3)
        self.register_stream_function(9, 5, self.register_callbacks.s09f5)
        self.register_stream_function(9, 7, self.register_callbacks.s09f7)
        self.register_stream_function(9, 9, self.register_callbacks.s09f9)
        self.register_stream_function(9, 11, self.register_callbacks.s09f11)

        self.handle_event = self.HandlerEvents(self)
        self.register_stream_function(6, 11, self.handle_event.events_receive)

        self.handle_alarm = self.HandlerAlarms(self)
        self.register_stream_function(5, 1, self.handle_alarm.s05f01)

        self.secs_control = self.SecsControl(self)

        self.register_stream_function(
            7, 3, self.secs_control.recipe_management.receive_recipe)

    def delayed_task(self):
        """
        Delayed task for subscribe lot
        """
        wait_seconds = 0.05
        logger.info("Task started, waiting for %s seconds...", wait_seconds)
        threading.Event().wait(wait_seconds)  # Non-blocking wait
        logger.info("%s seconds have passed!\n", wait_seconds)

        self.secs_control.get_control_state()
        # subscribe lot control
        # self.fc_control.subscribe_lot_control()

    def _on_state_communicating(self, _):

        super()._on_state_communicating(_)
        current_state = self.communicationState.current
        logger.info("%s On communication state: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)

        # Start the thread
        thread = threading.Thread(target=self.delayed_task)
        thread.start()

    def on_connection_closed(self, connection):
        super().on_connection_closed(connection)

        current_state = self.communicationState.current
        logger.info("%s On connection close: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)

    def _on_state_disconnect(self):
        super()._on_state_disconnect()

        current_state = "NOT_COMMUNICATING"
        logger.info("%s On state disconnect: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)

    def _on_hsms_packet_received(self, packet):
        decode = self.secs_decode(packet)
        self.mqtt_client.client.publish(
            f"equipments/status/secs_message/{self.equipment_name}", str(decode))
        return super()._on_hsms_packet_received(packet)

    commLogFileHandler = CommunicationLogFileHandler("logs/gem")
    commLogFileHandler.setFormatter(
        logging.Formatter('%(asctime)s: %(message)s'))
    logging.getLogger("hsms_communication").addHandler(commLogFileHandler)
    logging.getLogger("hsms_communication").propagate = False

    # Configure basic logging format and level
    logging.basicConfig(
        format='%(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.INFO)

    class CustomStreamFunction:
        """
        Class for custom stream functions
        """
        class SecsS02F49(SecsStreamFunction):
            """
            host command - send.

            **Data Items**
            - :class:`DATAID <secsgem.secs.dataitems.DATAID>`
            - :class:`OBJSPEC <secsgem.secs.dataitems.OBJSPEC>`
            - :class:`RCMD <secsgem.secs.dataitems.RCMD>`
            - :class:`CPNAME <secsgem.secs.dataitems.CPNAME>`
            - :class:`CPVAL <secsgem.secs.dataitems.CPVAL>`

            **Structure**::

                >>> import secsgem
                >>> secsgem.SecsS02F49
                {
                    DATAID: U4
                    OBJSPEC: A
                    RCMD: U1/I1/A
                    PARAMS: [
                        {
                            CPNAME: U1/U2/U4/U8/I1/I2/I4/I8/A
                            CPVAL: BOOLEAN/U1/U2/U4/U8/I1/I2/I4/I8/A/B
                        }
                        ...
                    ]
                }

            **Example**::

                >>> import secsgem
                >>> secsgem.SecsS02F49({DATAID": 123,OBJSPEC": "OBJ","RCMD": "ADD_LOT", "PARAMS": [{"CPNAME": "LotID", "CPVAL": "lot001"}]})
                S2F49 W
                <L [2]
                    <U 123>
                    <A "OBJ">
                    <A "ADD_LOT">
                    <L [2]
                    <L [2]
                        <A "LotID">
                        <A "lot001">
                    >
                    >
                > .

            :param value: parameters for this function (see example)
            :type value: list
            """

            _stream = 2
            _function = 49

            _dataFormat = [
                DATAID,
                OBJSPEC,
                RCMD,
                [
                    [
                        "PARAMS",   # name of the list
                        CPNAME,
                        CPVAL
                    ]
                ]
            ]

            _toHost = False
            _toEquipment = True

            _hasReply = True
            _isReplyRequired = True

            _isMultiBlock = False

        class SecsS02F50(SecsStreamFunction):
            """
            host command - acknowledge.

            **Data Items**

            - :class:`HCACK <secsgem.secs.dataitems.HCACK>`
            - :class:`CPNAME <secsgem.secs.dataitems.CPNAME>`
            - :class:`CPACK <secsgem.secs.dataitems.CPACK>`

            **Structure**::

                >>> import secsgem
                >>> secsgem.SecsS02F50
                {
                    HCACK: B[1]
                    PARAMS: [
                        {
                            CPNAME: U1/U2/U4/U8/I1/I2/I4/I8/A
                            CPACK: B[1]
                        }
                        ...
                    ]
                }

            **Example**::

                >>> import secsgem
                >>> secsgem.SecsS02F50({ \
                    "HCACK": secsgem.HCACK.INVALID_COMMAND, \
                    "PARAMS": [ \
                        {"CPNAME": "PARAM1", "CPACK": secsgem.CPACK.CPVAL_ILLEGAL_VALUE}, \
                        {"CPNAME": "PARAM2", "CPACK": secsgem.CPACK.CPVAL_ILLEGAL_FORMAT}]})
                S2F50
                <L [2]
                    <B 0x1>
                    <L [2]
                    <L [2]
                        <A "PARAM1">
                        <B 0x2>
                    >
                    <L [2]
                        <A "PARAM2">
                        <B 0x3>
                    >
                    >
                > .

            :param value: parameters for this function (see example)
            :type value: list
            """

            _stream = 2
            _function = 50

            _dataFormat = [
                HCACK,
                [
                    [
                        "PARAMS",   # name of the list
                        CPNAME,
                        CPACK
                    ]
                ]
            ]

            _toHost = True
            _toEquipment = False

            _hasReply = False
            _isReplyRequired = False

            _isMultiBlock = False

    class CommunicationCallbacks:
        """
        Class for handling communication callbacks
        """

        def __init__(self, equipment: "Equipment"):
            self.equipment = equipment

        def s01f14(self, handle, packet):
            """
            Handle S01F14
            """
            logger.info("<<-- S01F14")
            # print("<<-- S01F14")

        def s09f1(self, handle, packet):
            logger.warning("s09f1:Unrecognized Device ID (UDN): %s",
                           self.equipment.equipment_name)

        def s09f3(self, handle, packet):
            logger.warning("s09f3:Unrecognized Stream Function (SFCD): %s",
                           self.equipment.equipment_name)

        def s09f5(self, handle, packet):
            logger.warning("s09f5:Unrecognized Function Type (UFN): %s",
                           self.equipment.equipment_name)

        def s09f7(self, handle, packet):
            logger.warning("s09f7:Illegal Data (IDN): %s",
                           self.equipment.equipment_name)

        def s09f9(self, handle, packet):
            logger.warning("s09f9:Transaction Timer Timeout (TTN): %s",
                           self.equipment.equipment_name)

        def s09f11(self, handle, packet):
            logger.warning("s09f11:Data Too Long (DLN): %s",
                           self.equipment.equipment_name)

    class HandlerEvents:
        """
        Class for handling events
        """

        def __init__(self, equipment: "Equipment"):
            self.equipment = equipment

        def events_receive(self, handler, packet: HsmsPacket):
            """
            Handle S06F11
            """
            self.equipment.send_response(self.equipment.stream_function(6, 12)(
                ACKC6.ACCEPTED), packet.header.system)
            decode = self.equipment.secs_decode(packet)
            ceid = decode.CEID.get()

            for rpt in decode.RPT:
                if rpt:
                    rptid = rpt.RPTID.get()
                    values = rpt.V.get()
                    try:
                        if rptid == 1000:
                            lot_id, pp_name = values
                            lot_id = lot_id.upper()
                            if not lot_id:
                                logger.warning(
                                    "Requsest validate lot but lot_id is empty")
                                return

                            request_recipe = lot_id.split(",")
                            if len(request_recipe) > 1 and request_recipe[1] == "RECIPE":
                                logger.info(
                                    "Equipment request Recipe with lot_id: %s", lot_id)
                                return

                            logger.info("Validate lot: %s on %s", lot_id,
                                        self.equipment.equipment_name)
                            validate_result = ValidateLot(
                                self.equipment.equipment_name, pp_name, lot_id)
                            print(validate_result.result)
                            if not validate_result.result.get("status"):
                                message = validate_result.result.get("message")
                                self.reject_lot(lot_id, message)
                                return
                            self.accept_lot(lot_id)

                        elif rptid == 1001:
                            lot_id, pp_name = values
                            lot_id = lot_id.upper()
                            self.lot_open(lot_id)
                        elif rptid == 1002:
                            lot_id, pp_name = values
                            lot_id = lot_id.upper()
                            self.lot_close(lot_id)
                        elif rptid == 1003:
                            self.recipe_init(values)
                        else:
                            logger.warning("Unknown RPTID: %s", rptid)
                    except Exception as e:
                        logger.error("Error handling event: %s", e)

        def recipe_init(self, pp_name: str):
            """
            Init recipe
            """

            # if type(pp_name) == list:
            if isinstance(pp_name, list):
                self.equipment.pp_name = pp_name[0]
                pp_name = pp_name[0]
                self.equipment.mqtt_client.client.publish(
                    f"equipments/status/pp_name/{self.equipment.equipment_name}", pp_name)

        def lot_open(self, lot_id: str):
            """
            Open lot
            """
            self.equipment.lot_active = lot_id
            logger.info("Open lot: %s on %s", lot_id,
                        self.equipment.equipment_name)
            self.equipment.mqtt_client.client.publish(
                f"equipments/status/lot_active/{self.equipment.equipment_name}", lot_id)

        def lot_close(self, lot_id: str):
            """
            Close lot
            """
            self.equipment.lot_active = None
            logger.info("Close lot: %s on %s", lot_id,
                        self.equipment.equipment_name)
            self.equipment.mqtt_client.client.publish(
                f"equipments/status/lot_active/{self.equipment.equipment_name}", "")

        def accept_lot(self, lot_id: str):
            """
            Accept lot based on equipment model
            """
            if self.equipment.equipment_model == "FCL":
                self.equipment.secs_control.lot_management.accept_lot_fcl(
                    lot_id)
            elif self.equipment.equipment_model == "FCLX":
                self.equipment.secs_control.lot_management.add_lot_fclx(lot_id)
            else:
                logger.error("Unknown equipment model: %s",
                             self.equipment.equipment_model)

        def reject_lot(self, lot_id: str, reason: str = "Reason"):
            """
            Reject lot based on equipment model
            """
            if self.equipment.equipment_model == "FCL":
                self.equipment.secs_control.lot_management.reject_lot_fcl(
                    lot_id)
            elif self.equipment.equipment_model == "FCLX":
                self.equipment.secs_control.lot_management.reject_lot_fclx(
                    lot_id, reason)
            else:
                logger.error("Unknown equipment model: %s, equipment_name: %s",
                             self.equipment.equipment_model, self.equipment.equipment_name)

    class HandlerAlarms:
        """
        Class for handling alarms
        """

        def __init__(self, equipment: "Equipment"):
            self.equipment = equipment

        def s05f01(self, handler, packet: HsmsPacket):
            """
            Handle S5F1
            """
            self.equipment.send_response(self.equipment.stream_function(5, 2)(
                ACKC5.ACCEPTED), packet.header.system)

            decode = self.equipment.secs_decode(packet)
            alarm_id = decode.ALID.get()
            alarm_cd = decode.ALCD.get()
            alarm_text = decode.ALTX.get()
            message = f"alid: {alarm_id}, alcd: {
                alarm_cd},Alarm Text: {alarm_text}"
            self.equipment.mqtt_client.client.publish(
                f"equipments/status/alarm/{self.equipment.equipment_name}", message)

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

            def equipment_ready(self):
                """
                equipment ready
                """
                if not self.equipment.is_enabled:  # Check if equipment is enabled
                    return {"status": False, "message": "Equipment is disabled"}
                if not self.equipment.communicationState.current == "COMMUNICATING":  # Check if equipment is communicating
                    return {"status": False, "message": "Equipment is not communicating"}
                return {"status": True, "message": "Equipment is ready"}

            def accept_lot_fcl(self, lot_id: str):
                """
                accept lot
                """
                eq_ready = self.equipment_ready()
                if not eq_ready.get("status"):
                    logger.error("Equipment not ready: %s",
                                 eq_ready.get("message"))
                    return {"status": False, "message": eq_ready.get("message")}

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
                eq_ready = self.equipment_ready()
                if not eq_ready.get("status"):
                    logger.error("Equipment not ready: %s",
                                 eq_ready.get("message"))
                    return {"status": False, "message": eq_ready.get("message")}

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
                eq_ready = self.equipment_ready()
                if not eq_ready.get("status"):
                    logger.error("Equipment not ready: %s",
                                 eq_ready.get("message"))
                    return {"status": False, "message": eq_ready.get("message")}

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
                eq_ready = self.equipment_ready()
                if not eq_ready.get("status"):
                    logger.error("Equipment not ready: %s",
                                 eq_ready.get("message"))
                    return {"status": False, "message": eq_ready.get("message")}

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

            def equipment_ready(self):
                """
                equipment ready
                """
                if not self.equipment.is_enabled:  # Check if equipment is enabled
                    return {"status": False, "message": "Equipment is disabled"}
                if not self.equipment.communicationState.current == "COMMUNICATING":  # Check if equipment is communicating
                    return {"status": False, "message": "Equipment is not communicating"}
                return {"status": True, "message": "Equipment is ready"}

            def pp_dir(self):
                """
                s7f19
                """
                if not self.equipment_ready().get("status"):
                    return self.equipment_ready()

                return self.equipment.get_process_program_list()

            def pp_request(self, ppid: str):
                """
                s7f5
                """
                if not self.equipment_ready().get("status"):
                    return self.equipment_ready()

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

                    # save to path recipe upload
                    path = f"{
                        RECIPE_DIR}/{self.equipment.equipment_model}/{self.equipment.equipment_name}/upload"
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
                    # save to path recipe update
                    path = f"{
                        RECIPE_DIR}/{self.equipment.equipment_model}/{self.equipment.equipment_name}/upload"
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
                if not self.equipment_ready().get("status"):
                    return self.equipment_ready()

                path = f"{
                    RECIPE_DIR}/{self.equipment.equipment_model}/{self.equipment.equipment_name}/current/{ppid}"
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
                if not self.equipment_ready().get("status"):
                    return self.equipment_ready()
                return self.equipment.delete_process_programs(ppids=[ppid])

            def pp_select(self, ppid: str):
                """
                select process program on exist in equipment
                ppid: process program id
                """
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

        def equipment_ready(self):
            """
            equipment ready
            """
            if not self.equipment.is_enabled:  # Check if equipment is enabled
                return {"status": False, "message": "Equipment is disabled"}
            if not self.equipment.communicationState.current == "COMMUNICATING":  # Check if equipment is communicating
                return {"status": False, "message": "Equipment is not communicating"}
            return {"status": True, "message": "Equipment is ready"}

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
                "pp_name": self.equipment.pp_name,
                "lot_active": self.equipment.lot_active
            }
            return equipment_status

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
            eq_ready = self.equipment_ready().get("status")
            if not eq_ready:
                return self.equipment_ready()

            response_code = self.equipment.go_online()
            response_message = self.equipment.secs_control.response_message.response_message_onlack(
                response_code)
            if response_code == 0:
                logger.info("Equipment online: %s",
                            self.equipment.equipment_name)
                return {"status": True, "message": "Equipment online"}
            else:
                logger.error("Equipment online: %s, Error: %s",
                             self.equipment.equipment_name, response_message)
                return {"status": False, "message": response_message}

        def offline(self):
            """
            Offline equipment
            """
            eq_ready = self.equipment_ready().get("status")
            if not eq_ready:
                return self.equipment_ready()
            try:

                response_code = self.equipment.go_offline()
                response_message = self.equipment.secs_control.response_message.response_message_oflack(
                    response_code)
                if response_code == 0:
                    logger.info("Equipment offline: %s",
                                self.equipment.equipment_name)
                    return {"status": True, "message": "Equipment offline"}
                else:
                    logger.error("Equipment offline: %s, Error: %s",
                                 self.equipment.equipment_name, response_message)
                    return {"status": False, "message": response_message}
            except Exception as e:
                logger.error("Error offline equipment: %s", e)
                return {"status": False, "message": "Error offline equipment"}

        def get_control_state(self):
            """
            get control state
            """
            eq_ready = self.equipment_ready().get("status")
            if not eq_ready:
                return self.equipment_ready()

            # 1 = Off-Line/Equipment Off-Line
            # 2 = Off-Line/Attempt On-Line
            # 3 = Off-Line/Host Off-Line
            # 4 = On-Line/Local
            # 5 = On-Line/Remote
            vid = {"FCL": 28, "FCLX": 4}
            state_message = {
                1: "Off-Line/Equipment Off-Line",
                2: "Off-Line/Attempt On-Line",
                3: "Off-Line/Host Off-Line",
                4: "On-Line/Local",
                5: "On-Line/Remote"
            }
            model_vid = vid.get(self.equipment.equipment_model)

            if self.equipment.equipment_model in ["FCL", "FCLX"]:
                try:
                    s1f3 = self.equipment.secs_decode(self.equipment.send_and_waitfor_response(
                        self.equipment.stream_function(1, 3)([model_vid]))).get()
                    if isinstance(s1f3, list):
                        self.equipment.mqtt_client.client.publish(
                            f"equipments/status/control_state/{self.equipment.equipment_name}", state_message.get(s1f3[0]))
                        return {"status": True, "message": state_message.get(s1f3[0])}
                except Exception as e:
                    logger.error("Error get control state: %s", e)
                    return {"status": False, "message": str(e)}
            else:
                return {"status": False, "message": "Invalid equipment model"}

        def req_equipment_status(self, svids: list[int]):
            """
            s1f3
            """
            eq_ready = self.equipment_ready().get("status")
            if not eq_ready:
                return self.equipment_ready()

            s1f4 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 3)(svids))
            return self.equipment.secs_decode(s1f4)

        def req_equipment_constant(self, ceids: list[int] = None):
            """
            s2f13
            """
            eq_ready = self.equipment_ready().get("status")
            if not eq_ready:
                return self.equipment_ready()

            s2f14 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 13)(ceids))
            return self.equipment.secs_decode(s2f14)

        def req_status_variable_namelist(self, svids: list[int] = None):
            """
            s1f11
            Comment: Host sends L:0 to request all SVIDs.
            """
            eq_ready = self.equipment_ready().get("status")
            if not eq_ready:
                return self.equipment_ready()

            s1f12 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 11)(svids))
            return self.equipment.secs_decode(s1f12)

        def req_equipment_constant_namelist(self, ecids: list[int] = None):
            """
            s2f29
            Comment: Host sends L:0 for all ECIDs
            """
            eq_ready = self.equipment_ready().get("status")
            if not eq_ready:
                return self.equipment_ready()

            s2f30 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 29)(ecids))
            return self.equipment.secs_decode(s2f30)

        def enable_events(self, ceids: list[int] = None):
            """
            s2f37 CEED=True
            Comment: n=0 means all CEIDs
            """
            eq_ready = self.equipment_ready().get("status")
            if not eq_ready:
                return self.equipment_ready()

            s2f38 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 37)({"CEED": True, "CEID": ceids}))
            return self.equipment.secs_decode(s2f38)

        def disable_events(self, ceids: list[int] = None):
            """
            s2f37 CEED=False
            Comment: n=0 means all CEIDs
            """
            eq_ready = self.equipment_ready().get("status")
            if not eq_ready:
                return self.equipment_ready()

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
            eq_ready = self.equipment_ready().get("status")
            if not eq_ready:
                return self.equipment_ready()

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
            eq_ready = self.equipment_ready().get("status")
            if not eq_ready:
                return self.equipment_ready()

            resp_unsubscribe = self.equipment.send_and_waitfor_response(self.equipment.stream_function(2, 33)(
                {"DATAID": 0, "DATA": [{"RPTID": report_id, "VID": []}]}))

            resp_ubsubscribe_code = self.equipment.secs_decode(
                resp_unsubscribe).get()
            resp_unscribe_message = self.equipment.secs_control.response_message.response_message_drack(
                resp_ubsubscribe_code)
            if resp_ubsubscribe_code != 0:
                return {"status": False, "message": resp_unscribe_message}

            return {"status": True, "message": "Event unsubscribed"}
