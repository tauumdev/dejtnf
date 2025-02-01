import cmd
from dataclasses import dataclass
import json
import logging
from typing import Dict, List, Optional, TypedDict, Union
import paho.mqtt.client as mqtt
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.secs.dataitems import ACKC6, ACKC5
from secsgem.hsms.packets import HsmsPacket
from secsgem.secs.functionbase import SecsStreamFunction
from secsgem.secs.dataitems import MDLN, SVID, SV, SVNAME, UNITS, COMMACK, OFLACK, ONLACK, ECID, ECV, EAC, TIME, ECNAME, ECMIN, \
    ECMAX, ECDEF, DATAID, RPTID, VID, DRACK, CEID, LRACK, CEED, ERACK, RCMD, CPNAME, CPVAL, HCACK, CPACK, ALCD, ALID, \
    ALTX, ACKC5, ALED, TIMESTAMP, EXID, EXTYPE, EXMESSAGE, EXRECVRA, ACKA, ERRCODE, ERRTEXT, DATALENGTH, GRANT6, DSID, \
    DVNAME, DVVAL, V, ACKC6, PPID, LENGTH, PPGNT, PPBODY, ACKC7, MHEAD, SHEAD, MEXP, EDID, TID, TEXT, ACKC10, MID, \
    IDTYP, FNLOC, FFROT, ORLOC, RPSEL, REFP, DUTMS, XDIES, YDIES, ROWCT, COLCT, NULBC, PRDCT, PRAXI, SDACK, MAPFT, \
    BCEQU, MLCL, GRNT1, RSINF, BINLT, MDACK, STRP, XYPOS, SDBIN, MAPER, DATLC, OBJSPEC, OBJTYPE, OBJID, ATTRID, \
    ATTRDATA, ATTRRELN, OBJACK

from src.utils.logger.gem_logger import CommunicationLogFileHandler
from src.utils.logger.app_logger import AppLogger

USE_MQTT = True


class ValidationConfig:
    """Class for validating package data based on equipment configuration"""

    class PackageData(TypedDict, total=False):
        package8digit: str
        use_operation_code: bool
        use_on_operation: bool
        use_lot_hold: bool
        selection_code: str
        data_with_selection_code: List[Dict[str, str]]

    class EquipmentData(TypedDict, total=False):
        equipment_name: str
        data: List["ValidationConfig.PackageData"]

    @dataclass
    class DataConfig:
        """Configuration data class"""
        success: Dict[str, str] = None
        use_operation_code: bool = False
        use_on_operation: bool = False
        use_lot_hold: bool = False
        operation_code: str = ""
        on_operation: str = ""
        type_validate: str = ""
        recipe_name: str = ""
        product_name: str = ""

        def __post_init__(self):
            self.success = {"status": False, "message": "Data not loaded yet"}

    def __init__(self, equipment_name: str, package_code: str):
        self.equipment_name = equipment_name
        self.package_code = package_code
        self.all_data = self._load_json()
        self.data = self.DataConfig()

        try:
            self._validate_package_code()
            found_equipment = self._find_equipment()

            if not found_equipment:
                self.data.success = {"status": False,
                                     "message": "Equipment not found"}
                return

            found_package = self._match_package(found_equipment)
            if not found_package:
                self.data.success = {"status": False,
                                     "message": "Package code not found"}
                return

            self._extract_package_data(found_package)

        except ValueError as e:
            self.data.success = {"status": False, "message": str(e)}

    def _load_json(self) -> Dict[str, List[EquipmentData]]:
        """Load JSON file and validate structure"""
        try:
            with open('files/dbvalidate.json', 'r') as file:
                data = json.load(file)
                if not isinstance(data.get("data"), list):
                    raise ValueError("Invalid structure in dbvalidate.json")
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            raise ValueError(f"Error loading dbvalidate.json: {e}")

    def _validate_package_code(self) -> None:
        """Check package code length"""
        if len(self.package_code) != 15:
            raise ValueError("Package code must be 15 characters long")

    def _generate_selection_code(self, selection_rules: str) -> str:
        """Create selection code based on selection rules"""
        if len(selection_rules) != 4 or not set(selection_rules).issubset({'0', '1'}):
            raise ValueError("Selection rules must be 4 binary digits")

        parts = [
            self.package_code[:8] if selection_rules[0] == '1' else "",
            self.package_code[11] if selection_rules[1] == '1' else "",
            self.package_code[12:14] if selection_rules[2] == '1' else "",
            self.package_code[14] if selection_rules[3] == '1' else ""
        ]
        return "".join(parts)

    def _find_equipment(self) -> Optional[EquipmentData]:
        """Find the equipment data from JSON"""
        for eq in self.all_data.get("data", []):
            if eq.get("equipment_name") == self.equipment_name:
                return eq
        return None

    def _match_package(self, equipment: EquipmentData) -> Optional[PackageData]:
        """Find the package data that matches the package_code"""
        for pkg in equipment.get("data", []):
            if pkg.get("package8digit") == self.package_code[:8]:
                return pkg
        return None

    def _extract_package_data(self, package: PackageData) -> None:
        """Extract and validate package data"""
        self.data.use_operation_code = package.get("use_operation_code", False)
        self.data.use_on_operation = package.get("use_on_operation", False)
        self.data.use_lot_hold = package.get("use_lot_hold", False)

        selection_rules = package.get("selection_code", "1111")
        try:
            expected_code = self._generate_selection_code(selection_rules)
        except ValueError as e:
            self.data.success = {"status": False,
                                 "message": f"Invalid selection rules: {e}"}
            return

        matched_item = next(
            (item for item in package.get("data_with_selection_code", [])
             if item.get("package_selection_code") == expected_code),
            None
        )

        if matched_item:
            self.data.operation_code = matched_item.get("operation_code", "")
            self.data.on_operation = matched_item.get("on_operation", "")
            self.data.type_validate = matched_item.get("type_validate", "")
            self.data.recipe_name = matched_item.get("recipe_name", "")
            self.data.product_name = matched_item.get("product_name", "")
            self.data.success = {"status": True,
                                 "message": "Data loaded successfully"}
        else:
            self.data.success = {
                "status": False, "message": "No matching package selection code found. Expected code: " + expected_code}


class LotInformation:
    def __init__(self, lot_number: str):
        self.lot_number = lot_number
        self.data = self._load_json()

    def _load_json(self) -> Dict:
        try:
            with open('files/lotdetail.json', 'r') as file:
                data = json.load(file)
                # Get first object's OutputLotInfo since data is wrapped in array
                return data[0].get('OutputLotInfo', [])
        except FileNotFoundError:
            raise FileNotFoundError("lotdetail.json not found")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in lotdetail.json")

    def _find_field(self, search_key: str, search_value: str) -> Union[str, None]:
        for field in self.data:
            if field.get(search_key) == search_value:
                return field.get('Value')
        return None

    def field_by_name(self, field_names: Union[str, List[str]]) -> Union[str, List[str], None]:
        if isinstance(field_names, str):
            return self._find_field('FieldName', field_names)
        elif isinstance(field_names, list):
            return [self._find_field('FieldName', name) for name in field_names]
        return None

    def field_by_desc(self, descriptions: Union[str, List[str]]) -> Union[str, List[str], None]:
        if isinstance(descriptions, str):
            return self._find_field('Description', descriptions)
        elif isinstance(descriptions, list):
            return [self._find_field('Description', desc) for desc in descriptions]
        return None


class MqttClient:
    def __init__(self):
        self.client = mqtt.Client()
        # self.client.enable_logger(logger)
        self.client.username_pw_set("Tum", "Tum1234565")
        self.client.on_connect = self.on_connect
        self.client.on_message = self._HandlerMessage(self).on_message
        self.client.on_disconnect = self.on_disconnect

        if USE_MQTT:
            self.client.connect("localhost", 1883, 60)
            self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback function for when the client receives a CONNACK response from the server.
        """
        if rc == 0:
            print("Connected to MQTT broker.")
            for topic in ["equipments/config/#", "equipments/control/#"]:
                self.client.subscribe(topic)
                print(f"Subscribed to topic: {topic}")
        else:
            print(f"Connection failed with result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """
        Callback function for when the client disconnects from the server.
        """
        if rc != 0:
            print("Unexpected disconnection. Reconnecting...")
            self.client.reconnect()
        else:
            print("Disconnected from MQTT broker")

    class _HandlerMessage:
        def __init__(self, mqtt_client_instant: "MqttClient"):
            self.mqtt_client = mqtt_client_instant

        def on_message(self, client, userdata, msg: mqtt.MQTTMessage):
            print(f"Received message: {msg.payload}")


class Equipment(secsgem.gem.GemHostHandler):

    def __init__(self, equipment_name, equipment_model, address, port, session_id, active, enable, mqtt_client_instant: MqttClient, custom_connection_handler=None):
        super().__init__(address, port, active, session_id,
                         equipment_name, custom_connection_handler)
        self.mqtt_client = mqtt_client_instant
        self.equipment_name = equipment_name
        self.equipment_model = equipment_model
        self.is_enabled = enable

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

    def _on_state_communicating(self, _):
        print("<<-- State Communicating")
        return super()._on_state_communicating(_)

    def _on_state_disconnect(self):
        print("<<-- State Disconnect")
        return super()._on_state_disconnect()

    def on_connection_closed(self, connection):
        print("<<-- Connection Closed")
        return super().on_connection_closed(connection)

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
        def __init__(self, equipment: "Equipment"):
            self.equipment = equipment

        def s01f14(self):
            """
            Handle S01F14
            """
            print("<<-- S01F14")

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
        def __init__(self, equipment: "Equipment"):
            self.equipment = equipment

        def events_receive(self, handler, packet: HsmsPacket):
            self.equipment.send_response(self.equipment.stream_function(6, 12)(
                ACKC6.ACCEPTED), packet.header.system)
            # print("<<-- S06F11")
            decode = self.equipment.secs_decode(packet)

            ceid = decode.CEID.get()

            for rpt in decode.RPT:
                if rpt:
                    rptid = rpt.RPTID.get()
                    values = rpt.V.get()
                    lot_id, pp_name = values

                    lot_id = lot_id.strip().upper()
                    pp_name = pp_name.strip()

                    try:
                        if rptid == 1000:
                            self.validate_lot(pp_name, lot_id)
                        elif rptid == 1001:
                            pass
                        elif rptid == 1002:
                            pass
                        else:
                            logger.error("Unknown RPTID: %s", rptid)
                            print(f"Unknown RPT ID: {rptid}")
                    except Exception as e:
                        logger.error("Error handling FCL event: %s", e)

        def lot_open(self, pp_name: str, lot_id: str):
            """
            Open lot
            """
            logger.info("Open lot: %s", lot_id)
            self.equipment.mqtt_client.client.publish(
                f"equipments/status/lot_active/{self.equipment.equipment_name}", lot_id)

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
                print(f"Unknown equipment model: {
                      self.equipment.equipment_model}")

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
                print(f"Unknown equipment model: {
                      self.equipment.equipment_model}")

        def validate_lot(self, pp_name: str, lot_id: str):
            """
            Validate lot
            """
            data_lot = LotInformation(lot_id)
            # print("Data lot: ", data_lot.__dict__)
            equipment_name = self.equipment.equipment_name
            lot_package_code = data_lot.field_by_name("SASSYPACKAGE")
            lot_operation_code = data_lot.field_by_name("OPERATION_CODE")
            lot_on_operation = data_lot.field_by_name("ON_OPERATION")
            lot_lot_hold = data_lot.field_by_name("LOT_STATUS")

            data_config = ValidationConfig(equipment_name, lot_package_code)

            if not data_config.data.success.get("status"):
                print("Error loading data config: ",
                      data_config.data.success.get("message"))
                self.reject_lot(
                    lot_id, data_config.data.success.get("message"))
                return

            cfg_use_operation_code = data_config.data.use_operation_code
            cfg_use_on_operation = data_config.data.use_on_operation
            cfg_use_lot_hold = data_config.data.use_lot_hold
            cfg_operation_code = data_config.data.operation_code
            cfg_on_operation = data_config.data.on_operation
            cfg_type_validate = data_config.data.type_validate
            cfg_recipe_name = data_config.data.recipe_name
            # cfg_product_name = data_config.data.product_name

            if cfg_use_operation_code:
                if cfg_operation_code != lot_operation_code:
                    print("Operation code not match")
                    print("Operation code: ", cfg_operation_code)
                    print("Lot operation code: ", lot_operation_code)
                    self.reject_lot(lot_id, "Operation code not match")
                    return
            if cfg_use_on_operation:
                if cfg_on_operation != lot_on_operation:
                    print("On operation not match")
                    print("On operation: ", cfg_on_operation)
                    print("Lot on operation: ", lot_on_operation)
                    self.reject_lot(lot_id, "On operation not match")
                    return
            if cfg_use_lot_hold:
                if lot_lot_hold == "HOLD":
                    print("Lot is on hold")
                    print("Lot status: ", lot_lot_hold)
                    self.reject_lot(lot_id, "Lot is on hold")

                    return
            if cfg_type_validate == "RECIPE":
                if cfg_recipe_name != pp_name:
                    print("Recipe name not match")
                    print("Recipe name: ", cfg_recipe_name)
                    print("PP name: ", pp_name)
                    self.reject_lot(lot_id, "Recipe name not match")
                    return

            self.accept_lot(lot_id)

    class HandlerAlarms:
        def __init__(self, equipment: "Equipment"):
            self.equipment = equipment

        def s05f01(self, handler, packet: HsmsPacket):
            """
            Handle S5F1
            """
            self.equipment.send_response(self.equipment.stream_function(5, 2)(
                ACKC5.ACCEPTED), packet.header.system)

            print("<<-- S05F01")

    class SecsControl:
        def __init__(self, equipment: "Equipment"):
            self.equipment = equipment
            self.recipe_management = self._RecipeManagement(self.equipment)
            self.lot_management = self._LotManagement(self.equipment)

        def response_message_rcmd(self, code: int):
            """
            Response message S2F42
            """
            # 0 - ok, completed
            # 1 - invalid command
            # 2 - cannot do now
            # 3 - parameter error
            # 4 - initiated for asynchronous completion
            # 5 - rejected, already in desired condition
            # 6 - invalid object

            message = {0: "OK", 1: "Invalid command", 2: "Cannot do now",
                       3: "Parameter error", 4: "Initiated for asynchronous completion",
                       5: "Rejected, already in desired condition", 6: "Invalid object"}
            return message.get(code, "Unknown code")

        class _LotManagement:
            def __init__(self, equipment: "Equipment"):
                self.equipment = equipment

            def accept_lot_fcl(self, lot_id: str):
                """
                accept lot
                """

                secs_cmd = {"RCMD": "LOT_ACCEPT", "PARAMS": [
                    {"CPNAME": "LotID", "CPVAL": lot_id}]}
                s2f42 = self.equipment.send_and_waitfor_response(
                    self.equipment.stream_function(2, 41)(secs_cmd))
                decode_s2f42 = self.equipment.secs_decode(s2f42)
                response_code = decode_s2f42.HCACK.get()
                response_message = self.equipment.secs_control.response_message_rcmd(
                    response_code)
                # print(f"Accept lot: {response_message}")
                return f"Accept lot: {response_message}"

            def reject_lot_fcl(self, lot_id: str):
                """
                reject lot
                """
                secs_cmd = {"RCMD": "LOT_REJECT", "PARAMS": [
                    {"CPNAME": "LotID", "CPVAL": lot_id}]}
                s2f42 = self.equipment.send_and_waitfor_response(
                    self.equipment.stream_function(2, 41)(secs_cmd))
                decode_s2f42 = self.equipment.secs_decode(s2f42)
                response_code = decode_s2f42.HCACK.get()
                response_message = self.equipment.secs_control.response_message_rcmd(
                    response_code)
                # print(f"Reject lot: {response_message}")
                return f"Reject lot: {response_message}"

            def add_lot_fclx(self, lot_id: str):
                """
                add lot fclx
                """
                s2f49 = self.equipment.send_and_waitfor_response(
                    self.equipment.stream_function(2, 49)({"DATAID": 123, "OBJSPEC": "OBJ", "RCMD": "ADD_LOT", "PARAMS": [{"CPNAME": "LotID", "CPVAL": lot_id}]}))
                return self.equipment.secs_decode(s2f49)

            def reject_lot_fclx(self, lot_id: str, reason: str):
                """
                reject lot fclx
                """
                s2f49 = self.equipment.send_and_waitfor_response(
                    self.equipment.stream_function(2, 49)({"DATAID": 101, "OBJSPEC": "LOTCONTROL", "RCMD": "REJECT_LOT", "PARAMS": [{"CPNAME": "LotID", "CPVAL": lot_id}, {"CPNAME": "LotID", "CPVAL": reason}]}))
                return self.equipment.secs_decode(s2f49)

        class _RecipeManagement:
            def __init__(self, equipment: "Equipment"):
                self.equipment = equipment

            def pp_dir(self):
                """
                s7f19
                """
                return self.equipment.get_process_program_list()

            def pp_request(self, pp_name: str):
                """
                s7f5
                """
                return self.equipment.request_process_program(ppid=pp_name)

            def pp_send(self, pp_name: str, pp_body: str):
                """
                s7f3
                """
                return self.equipment.send_process_program(ppid=pp_name, ppbody=pp_body)

            def pp_delete(self, pp_name: str):
                """
                s7f17
                """
                return self.equipment.delete_process_programs(ppids=[pp_name])

        def req_equipment_status(self, svids: list[int]):
            """
            s1f3
            """
            s1f4 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 3)(svids))
            return self.equipment.secs_decode(s1f4)

        def req_equipment_constant(self, ceids: list[int] = None):
            """
            s2f13
            """
            s2f14 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 13)(ceids))
            return self.equipment.secs_decode(s2f14)

        def req_constant_namelist(self, ecids: list[int] = None):
            """
            s2f29
            """
            s2f30 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 29)(ecids))
            return self.equipment.secs_decode(s2f30)

        def enable_events(self, ceids: list[int] = None):
            """
            s2f37 CEED=True
            """
            s2f38 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 37)({"CEED": True, "CEID": ceids}))
            return self.equipment.secs_decode(s2f38)

        def disable_events(self, ceids: list[int] = None):
            """
            s2f37 CEED=False
            """
            s2f38 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 37)({"CEED": False, "CEID": ceids}))
            return self.equipment.secs_decode(s2f38)

        def subscribe_events(self, ceid: int, dvs: list[int], report_id: int = None):
            """
            s2f33
            """
            return self.equipment.subscribe_collection_event(ceid=ceid, dvs=dvs, report_id=report_id)

        def unsubscribe_events(self, report_id: list[int] = None):
            """
            s2f35
            """
            s2f36 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 35)({"DATAID": 0, "DATA": report_id}))
            return self.equipment.secs_decode(s2f36)


class EquipmentManager:
    def __init__(self, mqtt_client_instant: MqttClient):
        self.mqtt_client = mqtt_client_instant
        self.equipments: list[Equipment] = []
        self.config = self.Config(self.equipments)
        self.control = self.Control(self.equipments)
        self.load_equipments()

    def load_equipments(self):
        eq_conf = {
            "equipments": [
                {
                    "equipment_name": "TNF-61",
                    "equipment_model": "FCL",
                    "address": "192.168.226.161",
                    "port": 5000,
                    "session_id": 61,
                    "active": True,
                    "enable": True
                }, {
                    "equipment_name": "TNF-62",
                    "equipment_model": "FCL",
                    "address": "192.168.226.162",
                    "port": 5000,
                    "session_id": 62,
                    "active": True,
                    "enable": False
                }, {
                    "equipment_name": "TNF-63",
                    "equipment_model": "FCL",
                    "address": "192.168.226.163",
                    "port": 5000,
                    "session_id": 63,
                    "active": True,
                    "enable": False
                }
            ]
        }

        try:
            for equipment in eq_conf.get("equipments", []):
                equipment = Equipment(equipment["equipment_name"], equipment["equipment_model"], equipment["address"],
                                      equipment["port"], equipment["session_id"], equipment["active"], equipment["enable"], self.mqtt_client)

                if equipment.is_enabled:
                    equipment.enable()

                self.equipments.append(equipment)
                print(f"Equipment {equipment.equipment_name} initialized")

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error initializing equipment: {e}")

    def emptyline(self):
        pass

    def exit(self):
        print("Exit program.")
        try:
            for equipment in self.equipments:
                try:
                    if equipment.is_enabled:
                        equipment.disable()
                except Exception as e:
                    print(f"Error disabling equipment: {e}")
            self.mqtt_client.client.loop_stop()
            self.mqtt_client.client.disconnect()
        except Exception as e:
            print(f"Error exiting program: {e}")

    def list_equipments(self):
        return json.dumps([{
            "name": equipment.equipment_name,
            "model": equipment.equipment_model,
            "ip": equipment.address,
            "enable": equipment.is_enabled
        } for equipment in self.equipments])

    class Config:
        def __init__(self, equipments: list[Equipment]):
            self.equipments = equipments

        def save(self):
            pass

        def add(self, equipment: Equipment):
            pass

        def remove(self, equipment_name: str):
            pass

    class Control:
        def __init__(self, equipments: list[Equipment]):
            self.equipments = equipments

        def enable(self, equipment_name: str):
            return

        def disable(self, equipment_name: str):
            pass

        def online(self, equipment_name: str):
            pass

        def offline(self, equipment_name: str):
            pass


class CommandCli(cmd.Cmd):
    def __init__(self, mqtt_client_instant: MqttClient):
        super().__init__()
        self.prompt = ">> "
        self.equipments = EquipmentManager(mqtt_client_instant)

    def emptyline(self):
        pass

    def do_list(self, _):
        equipment_list = self.equipments.list_equipments()
        for equipment in json.loads(equipment_list):
            print(equipment)

    def do_exit(self, _):
        self.equipments.exit()
        return True


app_logger = AppLogger()
logger = app_logger.get_logger()
logger.setLevel(logging.INFO)

if __name__ == "__main__":
    mqtt_client = MqttClient()
    cli = CommandCli(mqtt_client)
    cli.cmdloop()

    # lot_info = LotInformation("MZ1PS0001.2")
    # print(lot_info.field_by_name("QTY"))
    # print(lot_info.field_by_name(["QTY", "LOT_STATUS"]))

    # print(lot_info.field_by_desc("Lot Qty"))
    # print(lot_info.field_by_desc(["Lot Qty", "LOT_STATUS"]))

    # vc = ValidationConfig("TNF-61", "LQFA048MS2GNSDM")
    # print(vc.data_config)
