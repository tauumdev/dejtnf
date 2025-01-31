import cmd
import json
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


class Equipment(secsgem.gem.GemHostHandler):
    def __init__(self, equipment_name, equipment_model, address, port, session_id, active, enable, custom_connection_handler=None):
        super().__init__(address, port, active, session_id,
                         equipment_name, custom_connection_handler)
        self.equipment_name = equipment_name
        self.equipment_model = equipment_model
        self.is_enabled = enable

        self.register_callbacks = self.CommunicationCallbacks(self)
        self.register_stream_function(1, 14, self.register_callbacks.s01f14)

        self.handle_event = self.HandlerEvents(self)
        self.register_stream_function(6, 11, self.handle_event.events_receive)

        self.handle_alarm = self.HandlerAlarms(self)
        self.register_stream_function(5, 1, self.handle_alarm.s05f01)

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

            print("type\n", type(decode))
            print("class\n", decode.__class__)
            print("dict\n", decode.__dict__)
            # ceid = decode.CEID.get()

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

        # json_data = eq_conf
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
