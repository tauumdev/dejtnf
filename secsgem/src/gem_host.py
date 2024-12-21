# gem_host.py
import logging
import os
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
import sys
import time
import paho.mqtt.client as mqtt

from src.fclx_event import FCLXEvent
from src.fcl_event import FCLEvent


class CommunicationLogFileHandler(logging.Handler):
    """Handler for logging communication to a file."""

    def __init__(self, path, prefix=""):
        super().__init__()
        self.path = path
        self.prefix = prefix

    def emit(self, record):
        filename = os.path.join(self.path, f"{self.prefix}com_{
                                record.address}.log")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "a", encoding="utf-8") as f:
            f.write(self.format(record) + "\n")


class DejtnfHost(secsgem.gem.GemHostHandler):
    """Host handler for DEJTNF."""

    def __init__(self, settings: secsgem.common.Settings, machine_name: str, mqtt_client: mqtt.Client):
        super().__init__(settings)
        self.machine_name = machine_name
        self.MDLN = "DEJTNF"
        self.SOFTREV = "1.0.0"
        self.enabled = False
        self.mqtt_client = mqtt_client
        self.register_stream_function(1, 14, self.s01f14)
        self.register_stream_function(9, 1, self.s09f1)
        self.register_stream_function(9, 3, self.s09f3)
        self.register_stream_function(9, 5, self.s09f5)
        self.register_stream_function(9, 7, self.s09f7)
        self.register_stream_function(9, 9, self.s09f9)
        self.register_stream_function(9, 11, self.s09f11)
        self._protocol.events.disconnected += self.on_connection_closed

    def s09f1(self, handle, packet):
        machine_model = getattr(self.settings, "machine_model", "unknown")
        print(f"{self.machine_name},{
              machine_model}, s09f1:Unrecognized Device ID (UDN)")

    def s09f3(self, handle, packet):
        machine_model = getattr(self.settings, "machine_model", "unknown")
        print(f"{self.machine_name},{
              machine_model}, s09f3:Unrecognized Stream Function (SFCD)")

    def s09f5(self, handle, packet):
        machine_model = getattr(self.settings, "machine_model", "unknown")
        print(f"{self.machine_name},{
              machine_model}, s09f5:Unrecognized Function Type (UFN)")

    def s09f7(self, handle, packet):
        machine_model = getattr(self.settings, "machine_model", "unknown")
        print(f"{self.machine_name},{machine_model}, s09f7:Illegal Data (IDN)")

    def s09f9(self, handle, packet):
        machine_model = getattr(self.settings, "machine_model", "unknown")
        print(f"{self.machine_name},{
              machine_model}, s09f9:Transaction Timer Timeout (TTN)")

    def s09f11(self, handle, packet):
        machine_model = getattr(self.settings, "machine_model", "unknown")
        print(f"{self.machine_name},{
              machine_model}, s09f11:Data Too Long (DLN)")

    def s01f14(self, handle, packet):
        self.mqtt_client.publish(
            f"hosts/{self.machine_name}/controlstate", "selected")

    def waitfor_communicating(self, timeout):
        machine_model = getattr(self.settings, "machine_model", "unknown")
        current_state = self._communication_state.current.name
        print(f"{self.machine_name},{
              machine_model}, waitfor_communicating, state: {current_state}")
        self.mqtt_client.publish(
            f"hosts/{self.machine_name}/communication", current_state)
        return super().waitfor_communicating(timeout)

    def on_commack_requested(self):
        machine_model = getattr(self.settings, "machine_model", "unknown")
        current_state = self._communication_state.current.name
        print(f"{self.machine_name},{
              machine_model}, on_commack_requested, state: {current_state}")
        self.mqtt_client.publish(
            f"hosts/{self.machine_name}/communication", current_state)
        return super().on_commack_requested()

    def _on_communicating(self, _):
        machine_model = getattr(self.settings, "machine_model", "unknown")
        current_state = self._communication_state.current.name
        print(f"{self.machine_name},{
              machine_model}, _on_communicating, state: {current_state}")
        self.mqtt_client.publish(
            f"hosts/{self.machine_name}/communication", current_state)
        return super()._on_communicating(_)

    def _on_state_communicating(self, _):
        machine_model = getattr(self.settings, "machine_model", "unknown")
        current_state = self._communication_state.current.name
        print(f"{self.machine_name},{
              machine_model}, _on_state_communicating, state: {current_state}")
        self.mqtt_client.publish(
            f"hosts/{self.machine_name}/communication", current_state)
        self.mqtt_client.publish(
            f"hosts/{self.machine_name}/controlstate", "selected")
        return super()._on_state_communicating(_)

    def on_connection_closed(self, _):
        machine_model = getattr(self.settings, "machine_model", "unknown")
        current_state = "NOT_COMMUNICATING"
        print(f"{self.machine_name},{
              machine_model}, on_connection_closed, state: {current_state}")
        self.mqtt_client.publish(
            f"hosts/{self.machine_name}/communication", current_state)
        return super().on_connection_closed(_)

    def enable_host(self, source="unknown"):
        """Enable the host."""
        if self.enabled:
            message = f"{self.machine_name} is already enabled."
            print(message)
            if source == "MQTT":
                self.mqtt_client.publish(
                    f"hosts/{self.machine_name}/commandresponse",
                    "already enabled")
            return

        print(f"{self.machine_name} is going enable by {source}.")
        try:
            self.enable()
            self.enabled = True
            message = f"{self.machine_name} is now enabled."
            print(message)
        except Exception as e:
            error_message = f"Error enabling {self.machine_name}: {e}"
            print(error_message)
            if source == "MQTT":
                self.mqtt_client.publish(
                    f"hosts/{self.machine_name}/commandresponse",
                    f"error: {e}")

    def disable_host(self, source="unknown"):
        """Disable the host."""
        if not self.enabled:
            message = f"{self.machine_name} is already disabled."
            print(message)
            if source == "MQTT":
                self.mqtt_client.publish(
                    f"hosts/{self.machine_name}/commandresponse",
                    "already disabled")
            return

        print(f"{self.machine_name} is going disable by {source}.")
        try:
            self.disable()
            self.enabled = False
            message = f"{self.machine_name} is now disabled."
            print(message)
        except Exception as e:
            error_message = f"Error disabling {self.machine_name}: {e}"
            print(error_message)
            if source == "MQTT":
                self.mqtt_client.publish(
                    f"hosts/{self.machine_name}/commandresponse",
                    f"error: {e}")

        current_state = self._communication_state.current.name
        self.mqtt_client.publish(
            f"hosts/{self.machine_name}/communication", current_state)

    def go_online(self, source="unknown"):
        """Transition the host to online state."""
        if not self.enabled:
            error_message = f"{
                self.machine_name} cannot go online because it is not enabled."
            print(error_message)
            if source == "MQTT":
                self.mqtt_client.publish(
                    f"hosts/{self.machine_name}/commandresponse", error_message)
            return False

        print(f"{self.machine_name} is going online by {source}.")
        try:
            response = self.settings.streams_functions.decode(
                self.send_and_waitfor_response(self.stream_function(1, 17)())
            )
            if response is None:
                print("No response received from the remote command.")
                if source == "MQTT":
                    self.mqtt_client.publish(
                        f"hosts/{self.machine_name}/commandresponse", "error: no response")
                return False

            response_code = {0x0: "ok", 0x1: "refused", 0x2: "already online"}
            response_message = response_code.get(
                response.get(), f"Unknown code: {response.get()}")
            print(f"Response message: {response_message}")
            if source == "MQTT":
                self.mqtt_client.publish(
                    f"hosts/{self.machine_name}/commandresponse", response_message)
            return response.get() == 0x0
        except Exception as e:
            print(f"Error during online transition: {e}")
            if source == "MQTT":
                self.mqtt_client.publish(
                    f"hosts/{self.machine_name}/commandresponse", f"error: {e}")
            return False

    def go_offline(self, source="unknown"):
        """Transition the host to offline state."""
        if not self.enabled:
            error_message = f"{
                self.machine_name} cannot go offline because it is not enabled."
            print(error_message)
            if source == "MQTT":
                self.mqtt_client.publish(
                    f"hosts/{self.machine_name}/commandresponse", error_message)
            return False

        print(f"{self.machine_name} is going offline by {source}.")
        try:
            response = self.settings.streams_functions.decode(
                self.send_and_waitfor_response(self.stream_function(1, 15)())
            )
            if response is None:
                print("No response received from the remote command.")
                if source == "MQTT":
                    self.mqtt_client.publish(
                        f"hosts/{self.machine_name}/commandresponse", "error: no response")
                return False

            response_code = {0x0: "ok", 0x1: "refused", 0x2: "already offline"}
            response_message = response_code.get(
                response.get(), f"Unknown code: {response.get()}")
            print(f"Response message: {response_message}")
            if source == "MQTT":
                self.mqtt_client.publish(
                    f"hosts/{self.machine_name}/commandresponse", response_message)
            return response.get() == 0x0
        except Exception as e:
            print(f"Error during offline transition: {e}")
            if source == "MQTT":
                self.mqtt_client.publish(
                    f"hosts/{self.machine_name}/commandresponse", f"error: {e}")
            return False

    def _on_alarm_received(self, handler, alarm_id, alarm_code, alarm_text):
        super()._on_alarm_received(handler, alarm_id, alarm_code, alarm_text)
        machine_model = getattr(self.settings, "machine_model", "unknown")
        print(f"{self.machine_name}, {machine_model} code: {
              alarm_code.get()} text: {alarm_text.get().strip()}")
        self.mqtt_client.publish(
            f"hosts/{self.machine_name}/alarm",
            f"{alarm_id.get()}:{alarm_code.get()} - {alarm_text.get().strip()}",
        )

    def _on_s06f11(self, handler, message):
        self.send_response(
            self.stream_function(6, 12)(
                secsgem.secs.data_items.ACKC6.ACCEPTED),
            message.header.system,
        )
        decode = self.settings.streams_functions.decode(message)
        machine_model = getattr(self.settings, "machine_model", "unknown")
        ceid = decode.CEID.get()
        if machine_model == "fcl":
            FCLEvent.handle_ceid(self, ceid, message)
        elif machine_model == "fclx":
            FCLXEvent.handle_ceid(self, ceid, message)
        else:
            print(f"unknow machine model: {machine_model}")


commLogFileHandler = CommunicationLogFileHandler("log")
commLogFileHandler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
logger = logging.getLogger("communication")
logger.setLevel(logging.DEBUG)
logger.addHandler(commLogFileHandler)
logger.propagate = False

# Remove default console handler if exists
root_logger = logging.getLogger()
root_logger.handlers = []

logging.basicConfig(
    format="%(asctime)s %(name)s.%(funcName)s: %(message)s", level=logging.ERROR
)
