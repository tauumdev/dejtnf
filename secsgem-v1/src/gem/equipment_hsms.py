import threading
import logging
import time
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.secs.dataitems import ACKC6, ACKC5
from secsgem.hsms.packets import HsmsPacket

from src.mqtt.mqtt_client_wrapper import MqttClient
from src.gem.custom_streamfunction import SecsS02F49, SecsS02F50
from src.handler.event_fcl import HandlerEventFcl
from src.handler.event_fclx import HandlerEventFclx
from src.handler.alarm_fcl import HandlerAlarmFCL
from src.handler.alarm_fclx import HandlerAlarmFCLX

logger = logging.getLogger("app_logger")


class Equipment(secsgem.gem.GemHostHandler):
    """
    Equipment class
    Attributes:
    - address: str
    - port: int
    - active: bool
    - session_id: int
    - name: str
    - equipment_model: str
    - is_enable: bool
    - mqtt_client: MqttClient
    - custom_connection_handler: None
    """

    def __init__(self, address, port: int, active: bool, session_id: int, name: str, equipment_model: str, is_enable: bool, mqtt_client: MqttClient, custom_connection_handler=None):

        super().__init__(address, port, active, session_id, name, custom_connection_handler)
        self.equipment_name = name
        self.equipment_model = equipment_model
        self.MDLN = "dejtnf"
        self.SOFTREV = "1.0.1"
        self.is_enabled = is_enable

        self.secsStreamsFunctions[2].update({49: SecsS02F49, 50: SecsS02F50})

        self.register_stream_function(1, 14, self.s01f14)
        self.register_stream_function(9, 1, self.s09f1)
        self.register_stream_function(9, 3, self.s09f3)
        self.register_stream_function(9, 5, self.s09f5)
        self.register_stream_function(9, 7, self.s09f7)
        self.register_stream_function(9, 9, self.s09f9)
        self.register_stream_function(9, 11, self.s09f11)

        self.mqtt_client = mqtt_client

        self.event_fcl = HandlerEventFcl(self)
        self.event_fclx = HandlerEventFclx(self)

        self.alarm_fcl = HandlerAlarmFCL(self)
        self.alarm_fclx = HandlerAlarmFCLX(self)

    def fcl_subscribe(self):
        """
        Subscribe lot control for FCL
        """
        self.disable_ceid_reports()
        self.subscribe_collection_event(
            20, [81, 33], 1000)  # LotValidate_LotID
        self.subscribe_collection_event(21, [82, 33], 1001)  # LotOpened_LotID
        self.subscribe_collection_event(22, [83, 33], 1002)  # LotClosed_LotID

    def fclx_subscribe(self):
        """
        Subscribe lot control for FCLX
        """
        self.disable_ceid_reports()
        self.subscribe_collection_event(
            20, [81, 33], 1000)  # LotValidate_LotID
        self.subscribe_collection_event(21, [82, 33], 1001)  # LotOpened_LotID
        self.subscribe_collection_event(22, [83, 33], 1002)  # LotClosed_LotID

    def delayed_task(self):
        """
        Delayed task for subscribe lot
        """
        wait_seconds = 0.1
        logger.info("Task started, waiting for %s seconds...", wait_seconds)
        threading.Event().wait(wait_seconds)  # Non-blocking wait
        logger.info("%s seconds have passed!\n", wait_seconds)

        try:

            offline_rsp = self.go_offline()
            offline_rsp_code = {0x0: "ok",
                                0x1: "refused", 0x2: "already offline"}
            logger.info("Offline response: %s, %s",
                        offline_rsp_code.get(offline_rsp, "unknown code"), self.equipment_name)
            time.sleep(wait_seconds)

            online_rsp = self.go_online()
            online_rsp_code = {0x0: "ok",
                               0x1: "refused", 0x2: "already offline"}
            logger.info("Online response: %s, %s",
                        online_rsp_code.get(online_rsp, "unknown code"), self.equipment_name)
            time.sleep(wait_seconds)

            if self.equipment_model == "FCL":
                logger.info("FCL %s Subscribe lot control.",
                            self.equipment_name)
                self.fcl_subscribe()
            elif self.equipment_model == "FCLX":
                logger.info("FCLX %s Subscribe lot control.",
                            self.equipment_name)
                self.fclx_subscribe()
            else:
                logger.info("Unknown equipment model")
        except Exception as e:
            logger.error("Error: %s", e)

    def _on_state_communicating(self, _):
        """
        Handle state communicating
        """
        super()._on_state_communicating(_)
        current_state = self.communicationState.current
        logger.info("%s On communication state: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)

        # Start the thread
        thread = threading.Thread(target=self.delayed_task)
        thread.start()
        # return super()._on_state_communicating(_)

    def on_connection_closed(self, connection):
        """
        Handle connection closed
        """
        super().on_connection_closed(connection)
        current_state = self.communicationState.current
        logger.info("%s On connection close: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)
        # return super().on_connection_closed(connection)

    def _on_state_disconnect(self):
        """
        Handle state disconnect
        """
        super()._on_state_disconnect()
        current_state = "NOT_COMMUNICATING"
        logger.info("%s On state disconnect: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)
        # return super()._on_state_disconnect()

    def _on_s01f13(self, handler, packet):
        """
        Handle S1F13
        """
        super()._on_s01f13(handler, packet)
        logger.info("Receive S1F13. %s", self.equipment_name)
        # return super()._on_s01f13(handler, packet)

    def s01f14(self, handler, packet: HsmsPacket):
        """
        Handle S1F14
        """
        logger.info("Receive S1F14. %s", self.equipment_name)

    def s09f1(self, handle, packet):
        logger.warning("s09f1:Unrecognized Device ID (UDN): %s",
                       self.equipment_name)

    def s09f3(self, handle, packet):
        logger.warning("s09f3:Unrecognized Stream Function (SFCD): %s",
                       self.equipment_name)

    def s09f5(self, handle, packet):
        logger.warning("s09f5:Unrecognized Function Type (UFN): %s",
                       self.equipment_name)

    def s09f7(self, handle, packet):
        logger.warning("s09f7:Illegal Data (IDN): %s",
                       self.equipment_name)

    def s09f9(self, handle, packet):
        logger.warning("s09f9:Transaction Timer Timeout (TTN): %s",
                       self.equipment_name)

    def s09f11(self, handle, packet):
        logger.warning("s09f11:Data Too Long (DLN): %s",
                       self.equipment_name)

    def _on_s05f01(self, handler, packet: HsmsPacket):
        """
        Handle S5F1
        """

        # first response
        self.send_response(self.stream_function(5, 2)(
            ACKC5.ACCEPTED), packet.header.system)

        s5f1 = self.secs_decode(packet)
        alid = s5f1.ALID.get()
        alcd = s5f1.ALCD.get()
        altx = s5f1.ALTX.get().strip()

        # define vid for FCL and FCLX
        vid = {'FCL': [82, 33], 'FCLX': [7, 40]}

        _model = self.equipment_model
        if _model in ['FCL', 'FCLX']:
            _vid = vid[_model]
            # Get PPName and Lot on operate
            s2f4 = self.send_and_waitfor_response(
                self.stream_function(1, 3)(_vid))
            decode_s2f4 = self.secs_decode(s2f4)

            lot_id, ppname = decode_s2f4

            if _model == "FCL":
                # handle alarm for FCL
                self.alarm_fcl.handle_alarm_fcl(
                    ppname.get(), lot_id.get(), alid, alcd, altx)
            elif _model == "FCLX":
                # handle alarm for FCLX
                self.alarm_fclx.handle_alarm_fclx(
                    ppname.get(), lot_id.get(), alid, alcd, altx)
        else:
            logger.warning("Unknown equipment model for %s",
                           self.equipment_model)

    def _on_s06f11(self, handler, packet: HsmsPacket):
        """
        Handle S6F11
        """
        self.send_response(self.stream_function(6, 12)(
            ACKC6.ACCEPTED), packet.header.system)

        if self.equipment_model == "FCL":
            # HandlerEventFcl.handle_s6f11(self, handler, packet)
            self.event_fcl.handle_s6f11(handler, packet)
        elif self.equipment_model == "FCLX":
            # HandlerEventFclx.handle_s6f11(self, handler, packet)
            self.event_fclx.handle_s6f11(handler, packet)
        else:
            logger.warning("Unknown equipment model for %s",
                           self.equipment_model)
