import cmd
import json
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


class MqttClient:
    def __init__(self):
        self.client = mqtt.Client()
        # self.client.enable_logger(logger)
        self.client.on_connect = self.on_connect
        self.client.on_message = self._HandlerMessage(self).on_message
        self.client.on_disconnect = self.on_disconnect

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
        def __init__(self, mqtt_client: "MqttClient"):
            self.mqtt_client = mqtt_client

        def on_message(self, client, userdata, msg: mqtt.MQTTMessage):
            print(f"Received message: {msg.payload}")


class Equipment(secsgem.gem.GemHostHandler):
    def __init__(self, equipment_name, equipment_model, address, port, session_id, active, enable, custom_connection_handler=None):
        super().__init__(address, port, active, session_id,
                         equipment_name, custom_connection_handler)
        self.equipment_name = equipment_name
        self.equipment_model = equipment_model
        self.is_enabled = enable

        self.custom_stream_function = self.CustomStreamFunction
        self.secsStreamsFunctions[2].update(
            {49: self.custom_stream_function.SecsS02F49, 50: self.custom_stream_function.SecsS02F50})

        self.register_callbacks = self.CommunicationCallbacks(self)
        self.register_stream_function(1, 14, self.register_callbacks.s01f14)

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

    class HandlerEvents:
        def __init__(self, equipment: "Equipment"):
            self.equipment = equipment

        def events_receive(self, handler, packet: HsmsPacket):
            self.equipment.send_response(self.equipment.stream_function(6, 12)(
                ACKC6.ACCEPTED), packet.header.system)
            print("<<-- S06F11")
            decode = self.equipment.secs_decode(packet)

            ceid = decode.CEID.get()
            print("CEID: ", ceid)

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

        class _LotManagement:
            def __init__(self, equipment: "Equipment"):
                self.equipment = equipment

            def accept_lot_fcl(self, lot_id: str):
                """
                accept lot
                """
                return self.equipment.send_remote_command({"RCMD": "LOT_ACCEPT", "PARAMS": [{"CPNAME": "LotID", "CPVAL": lot_id}]})

            def reject_lot_fcl(self, lot_id: str):
                """
                reject lot
                """
                return self.equipment.send_remote_command({"RCMD": "LOT_REJECT", "PARAMS": [{"CPNAME": "LotID", "CPVAL": lot_id}]})

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
    def __init__(self):
        self.equipments: list[Equipment] = []
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
                                      equipment["port"], equipment["session_id"], equipment["active"], equipment["enable"])

                if equipment.is_enabled:
                    equipment.enable()

                self.equipments.append(equipment)
                print("Equipment %s initialized",
                      equipment.equipment_name)

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
        except Exception as e:
            print(f"Error exiting program: {e}")

    def list_equipments(self):
        return [equipment.equipment_name for equipment in self.equipments]


class CommandCli(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.prompt = ">> "
        self.equipments = EquipmentManager()

    def do_list(self, _):
        print(self.equipments.list_equipments())

    def do_exit(self, _):
        self.equipments.exit()
        return True


if __name__ == "__main__":
    cli = CommandCli()
    cli.cmdloop()
