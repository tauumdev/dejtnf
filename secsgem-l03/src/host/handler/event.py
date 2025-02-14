import logging
import threading
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
from secsgem.secs.data_items import ACKC6

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.mqtt.mqtt_client import MqttClient
    from src.host.gemhost import SecsGemHost

from config.status_variable_define import CONTROL_STATE_EVENT, PROCESS_STATE_NAME

logger = logging.getLogger("app_logger")


class HandlerEvent:
    """
    Class for handling events
    """

    def __init__(self, gem_host: 'SecsGemHost'):
        self.gem_host = gem_host

    def receive_event(self, handler: secsgem.secs.SecsHandler, message: secsgem.common.Message):
        """
        Method for receiving event
        """
        handler.send_response(self.gem_host.stream_function(
            6, 12)(ACKC6.ACCEPTED), message.header.system)
        decode = self.gem_host.settings.streams_functions.decode(message)

        for rpt in decode.RPT:
            if rpt:
                rptid = rpt.RPTID.get()
                values = rpt.V.get()
                # print(f"RPTID: {rptid}")
                # print(f"Values: {values}")

                if rptid == 1000:
                    threading.Timer(0.05, self._req_validate_lot,
                                    args=[values]).start()
                if rptid == 1001:
                    self._lot_open(values)
                if rptid == 1002:
                    self._lot_close(values)
                if rptid == 1003:
                    self._process_program_change(values)
                if rptid == 1004:
                    self._process_state_change(values)

        ceid = decode.CEID.get()

        self._control_state(ceid)

    def _req_validate_lot(self, values: list):
        """
        Validate lot event
        """
        print(
            f"Equipment: {self.gem_host.equipment_name} request validate lot")
        if values:
            if len(values) == 2:
                lot_id, ppid = values
                if lot_id:
                    print(f"Lot ID: {lot_id}, PPID: {ppid}")
                    self.gem_host.secs_control.accept_lot(lot_id.upper())
                    return
                print("Lot ID is empty")

    def _lot_open(self, values: list):
        """
        Lot open event
        """
        print(f"Equipment: {self.gem_host.equipment_name} lot open")
        if values:
            if len(values) == 2:
                lot_id, ppid = values
                self.gem_host.active_lot = lot_id
                self.gem_host.mqtt_client.client.publish(
                    f"equipments/status/active_lot/{self.gem_host.equipment_name}", self.gem_host.active_lot, retain=True)
                print(f"Lot ID: {lot_id}, PPID: {ppid}")

    def _lot_close(self, values: list):
        """
        Lot close event
        """
        print(f"Equipment: {self.gem_host.equipment_name} lot close")
        if values:
            if len(values) == 2:
                lot_id, ppid = values
                self.gem_host.active_lot = None
                self.gem_host.mqtt_client.client.publish(
                    f"equipments/status/active_lot/{self.gem_host.equipment_name}", self.gem_host.active_lot, retain=True)
                print(f"Lot ID: {lot_id}, PPID: {ppid}")

    def _control_state(self, ceid: int):
        """
        Control state event
        """

        control_state = CONTROL_STATE_EVENT.get(
            self.gem_host.equipment_model, {}).get(ceid)
        if control_state:
            self.gem_host.control_state = control_state
            self.gem_host.mqtt_client.client.publish(
                f"equipments/status/control_state/{self.gem_host.equipment_name}", self.gem_host.control_state, retain=True)

    def _process_program_change(self, values: list):
        """
        Process program change event
        """
        if values:
            self.gem_host.process_program = values[0]
            self.gem_host.mqtt_client.client.publish(
                f"equipments/status/process_program/{self.gem_host.equipment_name}", self.gem_host.process_program, retain=True)

    def _process_state_change(self, values: list):
        """
        Process state change event
        """
        if values:
            model_state = PROCESS_STATE_NAME.get(
                self.gem_host.equipment_model, {})
            if not model_state:
                return
            state_name = model_state.get(values[0])
            if not state_name:
                return
            self.gem_host.process_state = state_name
            self.gem_host.mqtt_client.client.publish(
                f"equipments/status/process_state/{self.gem_host.equipment_name}", self.gem_host.process_state, retain=True)
