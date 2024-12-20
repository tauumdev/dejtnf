#gem_host.py
import logging
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
import sys
import os
import paho.mqtt.client as mqtt
import time

class CommunicationLogFileHandler(logging.Handler):
    def __init__(self, path, prefix=""):
        logging.Handler.__init__(self)
        self.path = path
        self.prefix = prefix

    def emit(self, record):
        filename = os.path.join(self.path, f"{self.prefix}com_{record.address}.log")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'a') as f:
            f.write(self.format(record) + "\n")

class DejtnfHost(secsgem.gem.GemHostHandler):
    def __init__(self, settings: secsgem.common.Settings, machine_name: str, mqtt_client: mqtt.Client):
        super().__init__(settings)
        self.machine_name = machine_name
        self.MDLN = "DEJTNF"
        self.SOFTREV = "1.0.0"
        self.enabled = False
        self.mqtt_client = mqtt_client
        self.register_stream_function(1,14,self.s01f14)
        self._protocol.events.disconnected += self.on_connection_closed

    def s01f14(self,handle,packet):
        machine_model = getattr(self.settings, 'machine_model', 'unknown')
        self.mqtt_client.publish(f"hosts/{self.machine_name}/controlstate", "selected")

    def waitfor_communicating(self, timeout):
        machine_model = getattr(self.settings, 'machine_model', 'unknown')
        current_state = self._communication_state.current.name

        print(f"{self.machine_name},{machine_model}, waitfor_communicating, state: {current_state}")
        self.mqtt_client.publish(f"hosts/{self.machine_name}/communication", current_state)

        return super().waitfor_communicating(timeout)
    
    def on_commack_requested(self):
        machine_model = getattr(self.settings, 'machine_model', 'unknown')
        current_state = self._communication_state.current.name

        print(f"{self.machine_name},{machine_model}, on_commack_requested, state: {current_state}")
        self.mqtt_client.publish(f"hosts/{self.machine_name}/communication", current_state)

        return super().on_commack_requested()    
    
    def _on_communicating(self, _):
        machine_model = getattr(self.settings, 'machine_model', 'unknown')
        current_state = self._communication_state.current.name

        print(f"{self.machine_name},{machine_model}, _on_communicating, state: {current_state}")
        self.mqtt_client.publish(f"hosts/{self.machine_name}/communication", current_state)

        return super()._on_communicating(_)
    
    def _on_state_communicating(self, _):
        machine_model = getattr(self.settings, 'machine_model', 'unknown')
        current_state = self._communication_state.current.name

        print(f"{self.machine_name},{machine_model}, _on_state_communicating, state: {current_state}")
        self.mqtt_client.publish(f"hosts/{self.machine_name}/communication", current_state)
        self.mqtt_client.publish(f"hosts/{self.machine_name}/controlstate", "selected")
        return super()._on_state_communicating(_)

    def on_connection_closed(self, _):
        machine_model = getattr(self.settings, 'machine_model', 'unknown')
        # current_state = self._communication_state.current.name
        current_state = "NOT_COMMUNICATING"

        print(f"{self.machine_name},{machine_model}, on_connection_closed, state: {current_state}")
        self.mqtt_client.publish(f"hosts/{self.machine_name}/communication", current_state)

        return super().on_connection_closed(_)
    
    def enable_host(self,source="unknown"):
        """_summary_

        Args:
            source (str, optional): _description_. Defaults to "unknown".
        """        
        if self.enabled:
            message = f"{self.machine_name} is already enabled."
            print(message)
            if source == "MQTT":
                self.mqtt_client.publish(f"hosts/{self.machine_name}/commandresponse", "already enabled")
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
                self.mqtt_client.publish(f"hosts/{self.machine_name}/commandresponse", f"error: {e}")

    def disable_host(self,source="unknown"):
        """_summary_

        Args:
            source (str, optional): _description_. Defaults to "unknown".
        """        
        if not self.enabled:
            message = f"{self.machine_name} is already disabled."
            print(message)
            if source == "MQTT":
                self.mqtt_client.publish(f"hosts/{self.machine_name}/commandresponse", "already disabled")
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
                self.mqtt_client.publish(f"hosts/{self.machine_name}/commandresponse", f"error: {e}")
        
        current_state = self._communication_state.current.name
        self.mqtt_client.publish(f"hosts/{self.machine_name}/communication", current_state)

    def go_online(self,source="unknown"):
        """_summary_

        Args:
            source (str, optional): _description_. Defaults to "unknown".

        Returns:
            _type_: _description_
        """        
        if not self.enabled:
            error_message = f"{self.machine_name} cannot go online because it is not enabled."
            print(error_message)
            if source == "MQTT":
                self.mqtt_client.publish(f"hosts/{self.machine_name}/commandresponse", error_message)

            return False  # Indicate failure to go online

        print(f"{self.machine_name} is going online by {source}.")

        # Send a remote command to transition online
        try:
            response = self.settings.streams_functions.decode(
                self.send_and_waitfor_response(self.stream_function(1, 17)())
            )

            if response is None:
                print("No response received from the remote command.")
                if source == "MQTT":
                    self.mqtt_client.publish(f"hosts/{self.machine_name}/commandresponse", "error: no response")

                return False

            # Define response codes for better readability
            response_code = {
                0x0: "ok",  # Successfully transitioned online
                0x1: "refused",  # Command refused by the system
                0x2: "already online",  # System is already in online state
            }

            # Retrieve response message
            response_message = response_code.get(response.get(), f"Unknown code: {response.get()}")
            print(f"Response message: {response_message}")

            if source == "MQTT":
                # Publish command response
                self.mqtt_client.publish(f"hosts/{self.machine_name}/commandresponse", response_message)

            return response.get() == 0x0  # Return True if the command succeeded

        except Exception as e:
            print(f"Error during online transition: {e}")
            if source == "MQTT":
                self.mqtt_client.publish(f"hosts/{self.machine_name}/commandresponse", f"error: {e}")

            return False

    def go_offline(self,source="unknown"):
        """_summary_

        Args:
            source (str, optional): _description_. Defaults to "unknown".

        Returns:
            _type_: _description_
        """        
        if not self.enabled:
            error_message = f"{self.machine_name} cannot go offline because it is not enabled."
            print(error_message)
            if source == "MQTT":
                self.mqtt_client.publish(f"hosts/{self.machine_name}/commandresponse", error_message)

            return False  # Indicate failure to go offline

        print(f"{self.machine_name} is going offline by {source}.")

        # Send a remote command to transition offline
        try:
            response = self.settings.streams_functions.decode(
                self.send_and_waitfor_response(self.stream_function(1, 15)())
            )

            if response is None:
                print("No response received from the remote command.")
                if source == "MQTT":
                    self.mqtt_client.publish(f"hosts/{self.machine_name}/commandresponse", "error: no response")

                return False

            # Define response codes for better readability
            response_code = {
                0x0: "ok",  # Successfully transitioned offline
                0x1: "refused",  # Command refused by the system
                0x2: "already offline",  # System is already in offline state
            }

            # Retrieve response message
            response_message = response_code.get(response.get(), f"Unknown code: {response.get()}")
            print(f"Response message: {response_message}")

            if source == "MQTT":
                # Publish command response
                self.mqtt_client.publish(f"hosts/{self.machine_name}/commandresponse", response_message)

            return response.get() == 0x0  # Return True if the command succeeded

        except Exception as e:
            print(f"Error during offline transition: {e}")
            if source == "MQTT":
                self.mqtt_client.publish(f"hosts/{self.machine_name}/commandresponse", f"error: {e}")

            return False

    def _on_alarm_received(self, handler, alarm_id, alarm_code, alarm_text):
        super()._on_alarm_received(handler, alarm_id, alarm_code, alarm_text)
        
        machine_model = getattr(self.settings, 'machine_model', 'unknown')
        print(f"{self.machine_name}, {machine_model} code: {alarm_code.get()} text: {alarm_text.get().strip()}")

        self.mqtt_client.publish(f"hosts/{self.machine_name}/alarm", f"{alarm_id.get()}:{alarm_code.get()} - {alarm_text.get().strip()}")

    def _on_s06f11(self, handler, message):
        self.send_response(self.stream_function(6, 12)(secsgem.secs.data_items.ACKC6.ACCEPTED), message.header.system)
        decode = self.settings.streams_functions.decode(message)
        machine_model = getattr(self.settings, 'machine_model', 'unknown')

        # print(f"decode: {decode}")
        # print(f"CEID: {decode.CEID}")
        # print(f"RPT: {decode.RPT}")
        ceid = decode.CEID.get()

        if machine_model == "fcl":
            if ceid in [8, 9, 10]:
                self.flc_handle_controlstate(ceid)

    def flc_handle_controlstate(self,ceid):
        """_summary_

        Args:
            ceid (_type_): _description_
        """        

        ceid_code = {
            8 : "offline",
            9 : "online/local",
            10 : "online/remote"
        }    
        _state = ceid_code.get(ceid, f"Unknown code: {ceid}")

        self.mqtt_client.publish(f"hosts/{self.machine_name}/controlstate", _state)

commLogFileHandler = CommunicationLogFileHandler("log")
commLogFileHandler.setFormatter(logging.Formatter("%(asctime)s: %(message)s"))
logger = logging.getLogger("communication")
logger.setLevel(logging.DEBUG)
logger.addHandler(commLogFileHandler)
logger.propagate = False

# Remove default console handler if exists
root_logger = logging.getLogger()
root_logger.handlers = []

logging.basicConfig(format='%(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.ERROR)
