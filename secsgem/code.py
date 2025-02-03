from dotenv import load_dotenv
import cmd
from dataclasses import dataclass
import ipaddress
import json
import logging
import os
import threading
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


class ValidationConfig:
    """Class for validating package data based on equipment configuration"""

    class PackageData(TypedDict, total=False):
        """Package data type"""
        package8digit: str
        use_operation_code: bool
        use_on_operation: bool
        use_lot_hold: bool
        selection_code: str
        data_with_selection_code: List[Dict[str, str]]

    class EquipmentData(TypedDict, total=False):
        """Equipment data type"""
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
            with open('files/dbvalidate.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                if not isinstance(data.get("data"), list):
                    logger.error("Invalid structure in dbvalidate.json")
                    # raise ValueError("Invalid structure in dbvalidate.json")
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error("Error loading dbvalidate.json: %s", e)

            # raise ValueError(f"Error loading dbvalidate.json: {e}") from e

    def _validate_package_code(self) -> None:
        """Check package code length"""
        if len(self.package_code.strip()) != 15:
            logger.error("Package code must be 15 characters long")
            print(self.package_code)
            raise ValueError("Package code must be 15 characters long")

    def _generate_selection_code(self, selection_rules: str) -> str:
        """Create selection code based on selection rules"""
        if len(selection_rules) != 4 or not set(selection_rules).issubset({'0', '1'}):
            logger.error("Selection rules must be 4 binary digits")
            # raise ValueError("Selection rules must be 4 binary digits")

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
        logger.error(
            "Equipment not found in configuration, equipment_name: %s", self.equipment_name)
        return None

    def _match_package(self, equipment: EquipmentData) -> Optional[PackageData]:
        """Find the package data that matches the package_code"""
        for pkg in equipment.get("data", []):
            if pkg.get("package8digit") == self.package_code[:8]:
                return pkg
        logger.error(
            "Package code not found in configuration, package_code: %s", self.package_code)
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
            logger.error("Invalid selection rules: %s", e)
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
            logger.error(
                "No matching package selection code found. Expected code: %s", expected_code)


class LotInformation:
    """
    Class for loading lot information from JSON
    """

    def __init__(self, lot_number: str):
        self.lot_number = lot_number
        self.success = False
        self.data = self._load_json()

    def _load_json(self) -> Dict:
        try:
            with open('files/lotdetail.json', 'r', encoding='utf-8') as file:
                data = json.load(file)
                if data[0].get("Status", True):
                    self.success = True
                else:
                    logger.error("Error loading lotdetail.json: %s",
                                 data[0].get("Message", "Unknown error"))
                # Get first object's OutputLotInfo since data is wrapped in array
                return data[0].get('OutputLotInfo', [])
        except FileNotFoundError:
            logger.error("lotdetail.json not found")
            # raise FileNotFoundError("lotdetail.json not found")
        except json.JSONDecodeError:
            logger.error("Invalid JSON format in lotdetail.json")
            # raise ValueError("Invalid JSON format in lotdetail.json")

    def _find_field(self, search_key: str, search_value: str) -> Union[str, None]:
        for field in self.data:
            if field.get(search_key) == search_value:
                return field.get('Value')
        return None

    def field_by_name(self, field_names: Union[str, List[str]]) -> Union[str, List[str], None]:
        """
        Get field value by field name
        Usage:
        field_by_name("FieldName")
        field_by_name(["FieldName1", "FieldName2"])
        """
        if isinstance(field_names, str):
            return self._find_field('FieldName', field_names)
        elif isinstance(field_names, list):
            return [self._find_field('FieldName', name) for name in field_names]
        logger.error("Invalid field_names type: %s", type(field_names))
        return None

    def field_by_desc(self, descriptions: Union[str, List[str]]) -> Union[str, List[str], None]:
        """
        Get field value by description
        Usage:
        field_by_desc("Description")
        field_by_desc(["Description1", "Description2"])
        """
        if isinstance(descriptions, str):
            return self._find_field('Description', descriptions)
        elif isinstance(descriptions, list):
            return [self._find_field('Description', desc) for desc in descriptions]
        logger.error("Invalid descriptions type: %s", type(descriptions))
        return None


class ValidateLot:
    """
    Class for validating lot information
    """

    def __init__(self, equipment_name: str, pp_name: str, lot_id: str):
        self.equipment_name = equipment_name
        self.pp_name = pp_name
        self.lot_id = lot_id
        self.data_lot = LotInformation(lot_id)
        self.data_config = ValidationConfig(
            equipment_name, self.data_lot.field_by_name("SASSYPACKAGE"))
        self.result = self._validate_lot()

    def _validate_lot(self):
        logger.info("Validating lot information")
        if not self.data_lot.success:
            logger.error("Error loading lot information")
            return {"status": False, "message": "Error loading lot information"}

        if not self.data_config.data.success:
            logger.error("Error loading configuration data")
            return {"status": False, "message": self.data_config.data.success.get("message")}

        # Dtat from lot information
        # lot_package_code = self.data_lot.field_by_name("SASSYPACKAGE")
        lot_operation_code = self.data_lot.field_by_name("OPERATION_CODE")
        lot_on_operation = self.data_lot.field_by_name("ON_OPERATION")
        lot_lot_hold = self.data_lot.field_by_name("LOT_STATUS")

        # Data from configuration
        cfg_operation_code = self.data_config.data.operation_code
        cfg_on_operation = self.data_config.data.on_operation
        cfg_type_validate = self.data_config.data.type_validate
        cfg_recipe_name = self.data_config.data.recipe_name

        # Optional configuration values
        cfg_use_operation_code = self.data_config.data.use_operation_code
        cfg_use_on_operation = self.data_config.data.use_on_operation
        cfg_use_lot_hold = self.data_config.data.use_lot_hold

        if cfg_type_validate.upper() == "RECIPE":
            if cfg_recipe_name != self.pp_name:
                logger.error("Invalid recipe name %s", self.pp_name)
                return {"status": False, "message": "Invalid recipe name"}
        if cfg_use_operation_code:
            if cfg_operation_code != lot_operation_code:
                logger.error("Invalid operation code %s", lot_operation_code)
                return {"status": False, "message": "Invalid operation code"}
        if cfg_use_on_operation:
            if cfg_on_operation != lot_on_operation:
                logger.error("Invalid on operation %s", lot_on_operation)
                return {"status": False, "message": "Invalid on operation"}
        if cfg_use_lot_hold:
            if lot_lot_hold == "HELD" or lot_lot_hold == "HOLD":
                logger.error("Lot is on hold, equipment_name")
                return {"status": False, "message": "Lot is on hold"}

        return {"status": True, "message": "Lot validated successfully"}


class MqttClient:
    """
    Class for handling MQTT client
    """
    # load environment variables
    load_dotenv()

    mqtt_enabled = os.getenv("MQTT_ENABLE")
    mqtt_broker = os.getenv("MQTT_BROKER")
    mqtt_port = int(os.getenv("MQTT_PORT"))
    mqtt_username = os.getenv("MQTT_USERNAME")
    mqtt_password = os.getenv("MQTT_PASSWORD")

    def __init__(self):
        self.client = mqtt.Client()
        # self.client.enable_logger(logger)
        self.client.username_pw_set(
            MqttClient.mqtt_username, MqttClient.mqtt_password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self._HandlerMessage(self).on_message
        self.client.on_disconnect = self.on_disconnect

        if MqttClient.mqtt_enabled:
            self.client.connect(MqttClient.mqtt_broker, 1883, 60)
            self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback function for when the client receives a CONNACK response from the server.
        """
        if rc == 0:
            logger.info("Connected to MQTT broker.")
            # print("Connected to MQTT broker.")
            for topic in ["equipments/config/#", "equipments/control/#"]:
                self.client.subscribe(topic)
                logger.info("Subscribed to topic: %s", topic)
                # print(f"Subscribed to topic: {topic}")
        else:
            logger.error("Connection failed with result code %s", rc)
            # print(f"Connection failed with result code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """
        Callback function for when the client disconnects from the server.
        """
        if rc != 0:
            # print("Unexpected disconnection. Reconnecting...")
            logger.warning("Unexpected disconnection. Reconnecting...")
            self.client.reconnect()
        else:
            logger.info("Disconnected from MQTT broker")
            # print("Disconnected from MQTT broker")

    class _HandlerMessage:
        """
        Class for handling MQTT messages
        """

        def __init__(self, mqtt_client_instant: "MqttClient"):
            self.mqtt_client = mqtt_client_instant

        def on_message(self, client, userdata, msg: mqtt.MQTTMessage):
            """
            Callback function for when a PUBLISH message is received from the server.
            """
            logger.info("Received message: %s", msg.payload)


class Equipment(secsgem.gem.GemHostHandler):
    """
    Class for handling equipment
    """

    def __init__(self, equipment_name, equipment_model, address, port, session_id, active, enable, mqtt_client_instant: MqttClient, custom_connection_handler=None):
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

    def delayed_task(self):
        """
        Delayed task for subscribe lot
        """
        wait_seconds = 0.05
        logger.info("Task started, waiting for %s seconds...", wait_seconds)
        threading.Event().wait(wait_seconds)  # Non-blocking wait
        logger.info("%s seconds have passed!\n", wait_seconds)

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
                                self.reject_lot(lot_id, "Lot ID is empty")
                                return

                            request_recipe = lot_id.split(",")
                            if len(request_recipe) > 1 and request_recipe[1] == "RECIPE":
                                print("Equipment request Recipe")
                                return

                            validate_result = ValidateLot(
                                self.equipment.equipment_name, pp_name, lot_id)

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
                    path = f"files/recipe/{self.equipment.equipment_model}/{
                        self.equipment.equipment_name}/upload/{ppid}"
                    self.create_dir(path)
                    with open(f"{path}/recipe.json", "w", encoding="utf-8") as f:
                        f.write(ppbody)
                    return {"status": True, "message": "Request recipe success on upload"}
                except Exception as e:
                    logger.error("Request recipe: %s on %s, Error: %s",
                                 ppid, self.equipment.equipment_name, e)
                    return {"status": False, "message": str(e)}

            def pp_send(self, ppid: str):
                """
                s7f3
                """
                if not self.equipment_ready().get("status"):
                    return self.equipment_ready()

                path = f"files/recipe/{self.equipment.equipment_model}/{
                    self.equipment.equipment_name}/current/{ppid}"
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


class EquipmentManager:
    """
    Equipment manager
    """

    def __init__(self, mqtt_client_instant: MqttClient):
        self.mqtt_client = mqtt_client_instant
        self.equipments: list[Equipment] = []
        self.config = self.Config(self.equipments)
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
        """
        Empty line
        """
        pass

    def exit(self):
        """
        Exit program
        """
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
        """
        List equipments
        """
        return json.dumps([{
            "name": equipment.equipment_name,
            "model": equipment.equipment_model,
            "ip": equipment.address,
            "enable": equipment.is_enabled
        } for equipment in self.equipments])

    class Config:
        """
        Equipment configuration
        """

        def __init__(self, equipments: list[Equipment]):
            self.equipments = equipments

        def save(self, path: str):
            """
            Save equipments to file
            """
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump([{
                        "equipment_name": equipment.equipment_name,
                        "equipment_model": equipment.equipment_model,
                        "address": equipment.address,
                        "port": equipment.port,
                        "session_id": equipment.sessionID,
                        "active": equipment.active,
                        "enable": equipment.is_enabled
                    } for equipment in self.equipments], f, indent=4)
            except Exception as e:
                return {"status": False, "message": f"Error saving equipments: {e}"}
            return {"status": True, "message": "Equipments saved"}

        def add(self, equipment: Equipment):
            """
            Add equipment
            """
            if equipment in self.equipments:
                # print(f"Equipment {equipment.equipment_name} already exists")
                return {"status": False, "message": "Equipment already exists"}
            if any(e.equipment_name == equipment.equipment_name and e.address == equipment.address
                   for e in self.equipments):
                # print(f"Equipment {equipment.name} already exists")
                return {"status": False, "message": "Equipment already exists"}

            if equipment.is_enabled:
                equipment.enable()
            self.equipments.append(equipment)
            return {"status": True, "message": "Equipment added"}

        def remove(self, equipment_name: str):
            """
            Remove equipment
            """
            equipment = next(
                (eq for eq in self.equipments if eq.equipment_name == equipment_name), None)
            if equipment:
                if equipment.is_enabled:
                    return {"status": False, "message": "Equipment is enabled and cannot be removed"}
                self.equipments.remove(equipment)
                return {"status": True, "message": "Equipment removed"}
            else:
                return {"status": False, "message": "Equipment not found"}


class CommandCli(cmd.Cmd):
    """
    Command line interface
    """

    def __init__(self, mqtt_client_instant: MqttClient):
        super().__init__()
        self.prompt = "dejtnf >> "
        self.equipments = EquipmentManager(mqtt_client_instant)

    def emptyline(self):
        pass

    def do_list(self, _):
        """
        List equipments
        Usage: list
        """
        equipment_list = self.equipments.list_equipments()
        for equipment in json.loads(equipment_list):
            print(equipment)

    def do_exit(self, _):
        """
        Exit program
        Usage: exit
        """
        self.equipments.exit()
        return True

    def do_config(self, _):
        """
        Equipment configuration command line interface
        Usage: config
        Function: Add, remove, list equipments
        """
        self.EquipmentConfigCli(self.equipments).cmdloop()

    def do_control(self, equipment_name: str):
        """
        Equipment control command line interface
        Usage: control <equipment_name>
        Function: enable, disable, online, offline, lot_accept, add_lot, subscribe_event, etc.
        """
        equipment = next(
            (eq for eq in self.equipments.equipments if eq.equipment_name == equipment_name), None)
        if equipment:
            self.EquipmentControlCli(equipment_name, equipment).cmdloop()
        else:
            print(f"Equipment {equipment_name} not found")
            print("List equipments to see available equipments")
            print("control <equipment_name>")

    class EquipmentConfigCli(cmd.Cmd):
        """
        Equipment configuration command line interface
        """

        def __init__(self,  equipments: EquipmentManager):
            super().__init__()
            self.prompt = "config >> "
            self.equipments = equipments

        def emptyline(self):
            pass

        def do_return(self, _):
            """
            Return to main menu
            Usage: return
            """
            return True

        def do_list(self, _):
            """
            List equipments
            Usage: list
            """
            equipment_list = self.equipments.list_equipments()
            for equipment in json.loads(equipment_list):
                print(equipment)

        def do_add(self, arg: str):
            """
            Add new equipment instance
            Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <active> <enable>
            Parameters:
                equipment_name (str): Equipment name.
                equipment_model (str): Equipment model.
                address (str): Equipment IP address.
                port (int): Equipment port number.
                session_id (int): Equipment session ID.
                active (bool): Equipment active status.
                enable (bool): Equipment enable status.
            """
            args = arg.split()
            if len(args) != 7:
                print("Invalid arguments")
                print(
                    "Usage: add <equipment_name> <equipment_model> <address> <port> <session_id> <active> <enable>")
                return

            try:
                equipment_name, equipment_model, address, port, session_id, active,  enable = args
                try:
                    ipaddress.ip_address(address)
                except ValueError:
                    logger.error("Invalid IP address")
                    print("Invalid IP address")
                    return
                active = active.lower() in ['true', '1', 't', 'y', 'yes']
                enable = enable.lower() in ['true', '1', 't', 'y', 'yes']

                equipment = Equipment(equipment_name, equipment_model, address,
                                      int(port), int(session_id), active, enable, self.equipments.mqtt_client)

                resp = self.equipments.config.add(equipment)
                if resp.get("status"):
                    print(f"Equipment {equipment_name} added")
                else:
                    print(f"Error adding equipment: {resp.get('message')}")
            except Exception as e:
                # logger.error("Error adding equipment")
                print("Error adding equipment")
                # logger.exception(e)
                print(e)

        def do_remove(self, equipment_name: str):
            """
            Remove equipment instance
            Usage: remove <equipment_name>
            Parameters:
                equipment_name (str): Equipment name.
            """
            print(self.equipments.config.remove(equipment_name))

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

            print(self.equipment.secs_control.online())

        def do_offline(self, _):
            """
            Go offline
            Usage: offline
            """

            print(self.equipment.secs_control.offline())

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

        # recipe management
        def do_pp_dir(self, _):
            """
            Process program directory
            Usage: pp_dir
            """
            print(self.equipment.secs_control.recipe_management.pp_dir())

        def do_pp_select(self, ppid: str):
            """
            Select process program
            Usage: pp_select <ppid>
            """
            if not ppid:
                print("Invalid arguments")
                print("Usage: pp_select <ppid>")
                return
            print(self.equipment.secs_control.recipe_management.pp_select(ppid))

        def do_pp_request(self, ppid: str):
            """
            Request process program
            Usage: pp_request <ppid>
            """
            if not ppid:
                print("Invalid arguments")
                print("Usage: pp_request <ppid>")
                return
            print(self.equipment.secs_control.recipe_management.pp_request(ppid))

        def do_pp_send(self, ppid: str):
            """
            Send process program
            Usage: pp_send <ppid>
            """
            if not ppid:
                print("Invalid arguments")
                print("Usage: pp_send <ppid>")
                return
            print(self.equipment.secs_control.recipe_management.pp_send(ppid))

        def do_pp_delete(self, ppid: str):
            """
            Delete process program
            Usage: pp_delete <ppid>
            """
            if not ppid:
                print("Invalid arguments")
                print("Usage: pp_delete <ppid>")
                return
            print(self.equipment.secs_control.recipe_management.pp_delete(ppid))


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
