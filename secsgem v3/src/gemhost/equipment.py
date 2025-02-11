import asyncio
import logging
import code
import os
import threading

import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.secs.data_items import ACKC6, ACKC5
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.mqtt.mqtt_client import MqttClient
from src.utils.config.status_variable_define import CONTROL_STATE_EVENT, CONTROL_STATE_VID, PP_CHANGE_EVENT, PROCESS_STATE_CHANG_EVENT, SUBSCRIBE_LOT_CONTROL, VID_PP_NAME

logger = logging.getLogger("app_logger")


class CommunicationLogFileHandler(logging.Handler):
    def __init__(self, path, prefix=""):
        logging.Handler.__init__(self)

        self.path = path
        self.prefix = prefix

    def emit(self, record):
        filename = os.path.join(self.path, "{}_{}_{}.log".format(
            self.prefix, record.address, record.session_id))
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(self.format(record) + "\n")


class SecsControl:
    """Secs control class"""

    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment

    def equipment_status(self):
        """Get equipment status"""

        status = {
            "equipment_name": self.equipment.equipment_name,
            "equipment_model": self.equipment.equipment_model,
            "address": getattr(self.equipment.settings, "address", None),
            "port": getattr(self.equipment.settings, "port", None),
            "session_id": self.equipment.settings.session_id,
            "is_enable": self.equipment.is_enable,
            "is_connected": self.equipment.is_connected,
            "control_state": self.control_state(),
            "process_state": self.process_state(),
            "process_program": self.process_program()
        }
        return status

    # communication control
    def enable(self):
        """Enable equipment"""
        if self.equipment.is_enable:
            return
        self.equipment.enable()
        self.equipment.is_enable = True

    def disable(self):
        """Disable equipment"""
        if not self.equipment.is_enable:
            return
        self.equipment.disable()
        self.equipment.is_enable = False

    def online(self):
        """Go online"""
        if not self.equipment.is_connected:
            return
        onack = {0: "ok", 1: "refused", 2: "already online"}
        response = self.equipment.settings.streams_functions.decode(
            self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 17)()),
        ).get()

        return onack.get(response, "Unknown Code: " + str(response))

    def offline(self):
        """Go offline"""
        if not self.equipment.is_connected:
            return
        offack = {0: "ok"}
        response = self.equipment.settings.streams_functions.decode(
            self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 15)()),
        ).get()

        return offack.get(response, "Unknown Code: " + str(response))

    def control_state(self):
        """Get control state"""
        if not self.equipment.is_connected:
            return
        vid_model = CONTROL_STATE_VID.get(self.equipment.equipment_model)
        if vid_model is None:
            return
        vid = vid_model.get("VID")
        state = vid_model.get("STATE")

        s1f4 = self.equipment.settings.streams_functions.decode(
            self.equipment.send_and_waitfor_response(self.equipment.stream_function(1, 3)([vid]))).get()
        if isinstance(s1f4, list):
            state_value = state.get(s1f4[0])
            self.equipment.control_state = state_value
            self.equipment.mqtt_client.client.publish(
                f"equipments/status/control_state/{self.equipment.equipment_name}", state_value)
            return state_value
        print(f"Failed to get control state: {s1f4}")

    def process_state(self):
        """Get process state"""
        if not self.equipment.is_connected:
            return
        vid_model = PROCESS_STATE_CHANG_EVENT.get(
            self.equipment.equipment_model)
        if vid_model is None:
            return
        vid = vid_model.get("VID")
        state = vid_model.get("STATE")

        s1f4 = self.equipment.settings.streams_functions.decode(
            self.equipment.send_and_waitfor_response(self.equipment.stream_function(1, 3)([vid]))).get()
        if isinstance(s1f4, list):
            state_value = next(
                (state_dict[s1f4[0]]
                 for state_dict in state if s1f4[0] in state_dict),
                # Default if code not found
                f"Unknown State ({s1f4[0]})"
            )
            self.equipment.process_state = state_value
            self.equipment.mqtt_client.client.publish(
                f"equipments/status/process_state/{self.equipment.equipment_name}", state_value)
            # print(f"Process state: {state_value}")
            return state_value
        print(f"Failed to get process state: {s1f4}")

    def process_program(self):
        """Get process program"""
        if not self.equipment.is_connected:
            return
        vid_model = VID_PP_NAME.get(
            self.equipment.equipment_model)
        if vid_model is None:
            return

        s1f4 = self.equipment.settings.streams_functions.decode(
            self.equipment.send_and_waitfor_response(self.equipment.stream_function(1, 3)([vid_model]))).get()
        if isinstance(s1f4, list):
            self.equipment.process_program = s1f4[0]
            self.equipment.mqtt_client.client.publish(
                f"equipments/status/process_program/{self.equipment.equipment_name}", s1f4[0])
            # print(f"Process program: {s1f4[0]}")
            return s1f4[0]
        print(f"Failed to get process program: {s1f4}")

    # get equipment status data
    def select_equipment_status_request(self, vids: list[int] = None):
        """
        S1F3R Select equipment status request
        """
        if not self.equipment.is_connected:
            return
        try:
            s1f4 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 3)(vids))
            if isinstance(s1f4, secsgem.hsms.message.HsmsMessage):
                # .get()
                return self.equipment.settings.streams_functions.decode(s1f4)
            return None
        except Exception as e:
            print(e)
            return None

    def status_variable_namelist_request(self, svids: list[int] = None):
        """
        S1F11R	Status Variable Namelist Request
        """
        if not self.equipment.is_connected:
            return
        try:
            s1f12 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 11)(svids))
            if isinstance(s1f12, secsgem.hsms.message.HsmsMessage):
                # .get()
                return self.equipment.settings.streams_functions.decode(s1f12)
            return None
        except Exception as e:
            print(e)
            return None

    def data_variable_namelist_request(self, vids: list[int] = None):
        """
        S1F21R	Data Variable Namelist Request
        """
        if not self.equipment.is_connected:
            return
        try:
            s2f22 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 21)(vids))
            if isinstance(s2f22, secsgem.hsms.message.HsmsMessage):
                # .get()
                return self.equipment.settings.streams_functions.decode(s2f22)
            return None
        except Exception as e:
            print(e)
            return None

    def collection_event_namelist_request(self, ceids: list[int] = None):
        """
        S1F23R	Collection Event Namelist Request
        """
        if not self.equipment.is_connected:
            return
        try:
            s1f24 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(1, 23)(ceids))
            if isinstance(s1f24, secsgem.hsms.message.HsmsMessage):
                # .get()
                return self.equipment.settings.streams_functions.decode(s1f24)
            return None
        except Exception as e:
            print(e)
            return None

    def equipment_constant_request(self, ecids: list[int] = None):
        """
        S2F13R	Equipment Constant Request
        """
        if not self.equipment.is_connected:
            return
        try:
            s2f14 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 13)(ecids))
            if isinstance(s2f14, secsgem.hsms.message.HsmsMessage):
                # .get()
                return self.equipment.settings.streams_functions.decode(s2f14)
            return None
        except Exception as e:
            print(e)
            return None

    def equipment_constant_namelist_request(self, ecids: list[int] = None):
        """
        S2F29R	Equipment Constant Namelist Request
        """
        if not self.equipment.is_connected:
            return
        try:
            s2f30 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 29)(ecids))
            if isinstance(s2f30, secsgem.hsms.message.HsmsMessage):
                # .get()
                return self.equipment.settings.streams_functions.decode(s2f30)
            return None
        except Exception as e:
            print(e)
            return None

    # event report
    def define_report(self, dvs: list[int], report_id: int):
        """
        2F33 Define Report
        """
        if not self.equipment.is_connected:
            return
        try:
            s2f34 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 33)({"DATAID": 0, "DATA": [{"RPTID": report_id, "VID": dvs}]}))
            if isinstance(s2f34, secsgem.hsms.message.HsmsMessage):
                _code = self.equipment.settings.streams_functions.decode(
                    s2f34).get()
                drack = {0: "ok", 1: "out of space", 2: "invalid format",
                         3: "1 or more RPTID already defined", 4: "1 or more invalid VID"}
                return drack.get(_code, "Unknown Code: " + str(_code))
            return None
        except Exception as e:
            print(e)
            return None

    def link_event_report(self, ceid: int, report_id: int):
        """
        2F35 Link Event Report
        """
        if not self.equipment.is_connected:
            return
        try:
            s2f36 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 35)({"DATAID": 0, "DATA": [{"CEID": ceid, "RPTID": [report_id]}]}))
            if isinstance(s2f36, secsgem.hsms.message.HsmsMessage):
                _code = self.equipment.settings.streams_functions.decode(
                    s2f36).get()
                lrack = {0: "ok", 1: "out of space", 2: "invalid format",
                         3: "1 or more CEID links already defined", 4: "1 or more CEID invalid", 5: "1 or more RPTID invalid"}
                return lrack.get(_code, "Unknown Code: " + str(_code))
            return None
        except Exception as e:
            print(e)
            return None

    def enable_disable_event(self, enable: bool, ceids: list[int] = None):
        """
        2F37 Enable/Disable Event Report
        """
        if not self.equipment.is_connected:
            return
        try:
            s2f38 = self.equipment.send_and_waitfor_response(
                self.equipment.stream_function(2, 37)({"CEED": enable, "CEID": ceids}))
            if isinstance(s2f38, secsgem.hsms.message.HsmsMessage):
                _code = self.equipment.settings.streams_functions.decode(
                    s2f38).get()
                return "ok" if _code == 0 else "denied"
            return None
        except Exception as e:
            print(e)
            return None

    def unsubscribe_event_report(self):
        """
        Unsubscribe to a collection event.
        """
        if not self.equipment.is_connected:
            return

        drack = {0: "ok", 1: "out of space", 2: "invalid format",
                 3: "1 or more RPTID already defined", 4: "1 or more invalid VID"}
        resp_unsubscribe = self.equipment.settings.streams_functions.decode(
            self.equipment.send_and_waitfor_response(self.equipment.stream_function(2, 33)(
                {"DATAID": 0, "DATA": []})))
        return drack.get(resp_unsubscribe.get(), "Unknown Code: " + str(resp_unsubscribe.get()))

    def subscribe_event_report(self, ceid: int, dvs: list[int], report_id: int):
        """
        Subscribe collection event report
        """
        if not self.equipment.is_connected:
            return
        try:
            # define report
            drack = self.define_report(dvs, report_id)
            if drack != "ok":
                print(f"Failed to define report: {drack}")
                return drack

            # link event report
            lrack = self.link_event_report(ceid, report_id)
            if lrack != "ok":
                print(f"Failed to link event report: {lrack}")
                return lrack

            # enable collection event
            erack = self.enable_disable_event(True, [ceid])
            if erack != "ok":
                print(f"Failed to enable event report: {erack}")
                return erack

            return f"Subscribed to CEID: {ceid} with RPTID: {report_id} and DVS: {dvs}"
        except Exception as e:
            print(e)
            return None

    def subscribe_lot_control(self):
        """Subscribe lot control"""
        if not self.equipment.is_connected:
            return
        subscribe = SUBSCRIBE_LOT_CONTROL.get(self.equipment.equipment_model)
        if subscribe is None:
            return
        for sub in subscribe:
            ceid = sub.get("CEID")
            dvs = sub.get("DVS")
            report_id = sub.get("report_id")
            if ceid and dvs and report_id:
                print(self.subscribe_event_report(ceid, dvs, report_id))


class ReceivedEvent:
    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment

    def receive_event(self, handler: secsgem.secs.SecsHandler, message: secsgem.common.Message):

        handler.send_response(self.equipment.stream_function(
            6, 12)(ACKC6.ACCEPTED), message.header.system)
        decode = self.equipment.settings.streams_functions.decode(message)
        # print(f"Message: {decode.get()}")

        for rpt in decode.RPT:
            if rpt:
                rptid = rpt.RPTID.get()
                values = rpt.V.get()
                print(f"RPTID: {rptid}")
                print(f"Values: {values}")

        ceid = decode.CEID.get()

        # control state
        control_state = CONTROL_STATE_EVENT.get(
            self.equipment.equipment_model, {}).get(ceid)
        if control_state:
            self.equipment.control_state = control_state
            self.equipment.mqtt_client.client.publish(
                f"equipments/status/control_state/{self.equipment.equipment_name}", control_state)

        # process state
        model_process_state = PROCESS_STATE_CHANG_EVENT.get(
            self.equipment.equipment_model, {})
        model_process_state_ceid = model_process_state.get("CEID")

        if model_process_state:
            if ceid == model_process_state_ceid:
                threading.Timer(
                    0.01, self.equipment.secs_control.process_state).start()

        # process program change
        model_pp_change = PP_CHANGE_EVENT.get(
            self.equipment.equipment_model, {})
        if model_pp_change:
            if ceid == model_pp_change.get("CEID"):
                threading.Timer(
                    0.01, self.equipment.secs_control.process_program).start()


class ReceivedAlarm:
    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment

    def receive_alarm(self, handler: secsgem.secs.SecsHandler, message: secsgem.common.Message):

        handler.send_response(self.equipment.stream_function(
            5, 2)(ACKC5.ACCEPTED), message.header.system)
        decode = self.equipment.settings.streams_functions.decode(message)
        # print(f"Message: {decode.get()}")


class Equipment(secsgem.gem.GemHostHandler):
    """Equipment class"""

    def __init__(self, equipment_name: str, equipment_model: str, enable: bool, mqtt_client: 'MqttClient', settings: secsgem.common.Settings):
        super().__init__(settings)
        self.mqtt_client = mqtt_client
        self.equipment_name = equipment_name
        self.equipment_model = equipment_model
        self.control_state = None
        self.process_state = None
        self.process_program = None
        self.active_lot = None
        self.is_enable = enable
        self.MDLN = "dejtnf-host"
        self.SOFTREV = "1.0.0"

        self.secs_control = SecsControl(self)
        self.received_event = ReceivedEvent(self)
        self.register_stream_function(6, 11, self.received_event.receive_event)
        self.received_alarm = ReceivedAlarm(self)
        self.register_stream_function(5, 1, self.received_alarm.receive_alarm)

        self.register_stream_function(9, 1, self.s09f1)
        self.register_stream_function(9, 3, self.s09f3)
        self.register_stream_function(9, 5, self.s09f5)
        self.register_stream_function(9, 7, self.s09f7)
        self.register_stream_function(9, 9, self.s09f9)
        self.register_stream_function(9, 11, self.s09f11)

        self._protocol.events.disconnected += self.on_connection_closed

        if self.is_enable:
            self.enable()

    @property
    def is_connected(self):
        """Check if equipment is connected"""
        return getattr(self._protocol, "_connected", False)

    def enable(self):
        if self.is_connected:
            return
        self.is_enable = True
        return super().enable()

    def disable(self):
        if not self.is_enable:
            return
        self.is_enable = False
        return super().disable()

    def _on_message_received(self, data):
        message = data["message"]
        self.mqtt_client.client.publish(
            f"equipments/status/secs_message/{self.equipment_name}", str(self.settings.streams_functions.decode(message)))
        return super()._on_message_received(data)

    def _on_state_communicating(self, _):
        super()._on_state_communicating(_)
        print("Equipment is state communicating")
        print("Communication state: ", self.communication_state.current.name)

        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", self.communication_state.current.name)

        threading.Timer(
            0.1, self.secs_control.unsubscribe_event_report).start()
        threading.Timer(0.1, self.secs_control.subscribe_lot_control).start()
        threading.Timer(0.1, self.secs_control.control_state).start()
        threading.Timer(0.1, self.secs_control.process_state).start()
        threading.Timer(0.1, self.secs_control.process_program).start()

    def _on_state_wait_cra(self, _):
        super()._on_state_wait_cra(_)
        print("Equipment is state wait cra")
        print("Communication state: ", self.communication_state.current.name)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", self.communication_state.current.name)

    def on_connection_closed(self, _):
        super().on_connection_closed(_)
        print("Equipment connection closed")
        print("Communication state: ", self.communication_state.current.name)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", self.communication_state.current.name)

    def s09f1(self, handle, packet):
        """Unrecognized Device ID"""
        logger.warning("s09f1:Unrecognized Device ID (UDN): %s",
                       self.equipment_name)
        print("s09f1:Unrecognized Device ID (UDN): %s",
              self.equipment_name)

    def s09f3(self, handle, packet):
        """Unrecognized Stream Function"""
        logger.warning("s09f3:Unrecognized Stream Function (SFCD): %s",
                       self.equipment_name)
        print("s09f3:Unrecognized Stream Function (SFCD): %s",
              self.equipment_name)

    def s09f5(self, handle, packet):
        """Unrecognized Function Type"""
        logger.warning("s09f5:Unrecognized Function Type (UFN): %s",
                       self.equipment_name)
        print("s09f5:Unrecognized Function Type (UFN): %s",
              self.equipment_name)

    def s09f7(self, handle, packet):
        """Illegal Data (IDN)"""
        logger.warning("s09f7:Illegal Data (IDN): %s",
                       self.equipment_name)
        print("s09f7:Illegal Data (IDN): %s",
              self.equipment_name)

    def s09f9(self, handle, packet):
        """Transaction Timer Timeout (TTN)"""
        logger.warning("s09f9:Transaction Timer Timeout (TTN): %s",
                       self.equipment_name)
        print("s09f9:Transaction Timer Timeout (TTN): %s",
              self.equipment_name)

    def s09f11(self, handle, packet):
        """Data Too Long (DLN)"""
        logger.warning("s09f11:Data Too Long (DLN): %s",
                       self.equipment_name)
        print("s09f11:Data Too Long (DLN): %s",
              self.equipment_name)


commLogFileHandler = CommunicationLogFileHandler("logs/gem")
commLogFileHandler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
logging.getLogger("communication").addHandler(commLogFileHandler)
logging.getLogger("communication").propagate = False

logging.basicConfig(
    format='%(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.INFO)
