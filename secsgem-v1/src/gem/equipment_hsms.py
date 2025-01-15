import threading
import logging
import time
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.secs.dataitems import ACKC6
from secsgem.hsms.packets import HsmsPacket

from src.mqtt.mqtt_client_wrapper import MqttClient
from src.handler.handler_fcl import HandlerFcl

logger = logging.getLogger("app_logger")


class Equipment(secsgem.gem.GemHostHandler):
    def __init__(self, address, port: int, active: bool, session_id: int, name: str, equipment_model: str, is_enable: bool, mqtt_client: MqttClient, custom_connection_handler=None):
        super().__init__(address, port, active, session_id, name, custom_connection_handler)
        self.equipment_name = name
        self.equipment_model = equipment_model
        self.MDLN = "dejtnf"
        self.SOFTREV = "1.0.1"
        self.is_enabled = is_enable

        self.register_stream_function(1, 14, self.s01f14)

        self.mqtt_client = mqtt_client

    def fcl_subscribe(self):
        self.disable_ceid_reports()
        self.subscribe_collection_event(
            20, [81, 33], 1000)  # LotValidate_LotID
        self.subscribe_collection_event(21, [82, 33], 1001)  # LotOpened_LotID
        self.subscribe_collection_event(22, [83, 33], 1002)  # LotClosed_LotID

    def fclx_subscribe(self):
        self.disable_ceid_reports()
        self.subscribe_collection_event(
            20, [81, 33], 1000)  # LotValidate_LotID
        self.subscribe_collection_event(21, [82, 33], 1001)  # LotOpened_LotID
        self.subscribe_collection_event(22, [83, 33], 1002)  # LotClosed_LotID

    def delayed_task(self):

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
        current_state = self.communicationState.current
        logger.info("%s On connection close: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)
        return super().on_connection_closed(connection)

    def _on_state_disconnect(self):
        current_state = "NOT_COMMUNICATING"
        logger.info("%s On state disconnect: %s",
                    self.equipment_name, current_state)
        self.mqtt_client.client.publish(
            f"equipments/status/communication_state/{self.equipment_name}", current_state, qos=1, retain=True)
        return super()._on_state_disconnect()

    def _on_s01f13(self, handler, packet):
        logger.info("Receive S1F13. %s", self.equipment_name)
        return super()._on_s01f13(handler, packet)

    def s01f14(self, handler, packet: HsmsPacket):
        logger.info("Receive S1F14. %s", self.equipment_name)

    def _on_s06f11(self, handler, packet: HsmsPacket):
        self.send_response(self.stream_function(6, 12)(
            ACKC6.ACCEPTED), packet.header.system)

        if self.equipment_model == "FCL":
            HandlerFcl.handle_s6f11(self, handler, packet)

        else:
            logger.info("Unknown equipment model")

        # decode = self.secs_decode(packet)
        # ceid = decode.CEID
        # if ceid == 20:
        #     # print(decode.CEID.get())
        #     self.send_remote_command(
        #         rcmd="LOT_ACCEPT", params=[["LotID", "123456"]])
