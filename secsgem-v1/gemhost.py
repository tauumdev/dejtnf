import cmd
import logging
import json
import os
import socket
import secsgem.common
import secsgem.gem
import secsgem.hsms
import paho.mqtt.client as mqtt
from src.fcl_handle import Fcl_handle

# Create the log directory if it doesn't exist
log_directory = "log"
# Creates the directory if it doesn't exist
os.makedirs(log_directory, exist_ok=True)

# Create a separate logger for command outputs (separate from the existing logging)
command_logger = logging.getLogger("command_logger")
command_logger.setLevel(logging.INFO)

# Create a file handler (or use StreamHandler for console output)
command_log_file = os.path.join(log_directory, "command_output.log")
file_handler = logging.FileHandler(command_log_file)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
command_logger.addHandler(file_handler)

# You can also add a console handler if you want to print to console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(message)s"))
# command_logger.addHandler(console_handler)

command_logger.info("Logging setup complete.")


class CommunicationLogFileHandler(logging.Handler):
    def __init__(self, path, prefix=""):
        logging.Handler.__init__(self)
        self.path = path
        self.prefix = prefix

    def emit(self, record):
        filename = os.path.join(self.path, "{}com_{}.log".format(
            self.prefix, record.remoteName))
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'a') as f:
            f.write(self.format(record) + "\n")


class SampleHost(secsgem.gem.GemHostHandler):
    def __init__(self, settings: secsgem.common.Settings, equipment_name: str, equipment_type: str, mqtt_client: mqtt.Client):
        super().__init__(settings)
        self.MDLN = "gemhost"
        self.SOFTREV = "1.0.0"
        self.equipment_name = equipment_name
        self.equipment_type = equipment_type
        self.mqtt_client = mqtt_client
        self._enabled = False  # Add this flag to manage equipment state

        # Create an instance of Fcl_handle
        self.fcl_handler = Fcl_handle(self)

        self.register_stream_function(1, 14, self._on_s01f14)
        self.register_stream_function(9, 1, self.s09f1)
        self.register_stream_function(9, 3, self.s09f3)
        self.register_stream_function(9, 5, self.s09f5)
        self.register_stream_function(9, 7, self.s09f7)
        self.register_stream_function(9, 9, self.s09f9)
        self.register_stream_function(9, 11, self.s09f11)
        self._protocol.events.disconnected += self.on_connection_closed

    def waitfor_communicating(self, timeout=None):
        current_state = self._communication_state.current.name
        command_logger.info(f"{self.equipment_name}, {
            self.equipment_type}, waitfor_communicating, state: {current_state}")
        return super().waitfor_communicating(timeout)

    def on_commack_requested(self):
        current_state = self._communication_state.current.name
        command_logger.info(f"{self.equipment_name}, {
            self.equipment_type}, on_commack_requested, state: {current_state}")
        return super().on_commack_requested()

    def _on_communicating(self, _):
        current_state = self._communication_state.current.name
        command_logger.info(f"{self.equipment_name}, {
            self.equipment_type}, _on_communicating, state: {current_state}")
        return super()._on_communicating(_)

    def _on_state_communicating(self, _):
        current_state = self._communication_state.current.name
        command_logger.info(f"{self.equipment_name}, {
            self.equipment_type}, _on_state_communicating, state: {current_state}")
        return super()._on_state_communicating(_)

    def on_connection_closed(self, _):
        # current_state = self._communication_state.current.name
        current_state = "NOT_COMMUNICATING"
        command_logger.info(f"{self.equipment_name}, {
            self.equipment_type}, on_connection_closed, state: {current_state}")
        return super().on_connection_closed(_)

    def _on_s01f13(self, handler, message):
        return super()._on_s01f13(handler, message)

    def _on_s01f14(self, handler, message):
        print("online")

    def _on_s05f01(self, handler, message):
        return super()._on_s05f01(handler, message)

    def _on_s06f11(self, handler, message):
        self.send_response(
            self.stream_function(6, 12)(
                secsgem.secs.data_items.ACKC6.ACCEPTED),
            message.header.system,
        )
        decode = self.settings.streams_functions.decode(message)
        ceid = decode.CEID.get()

        if self.equipment_type == "fcl":
            # Delegate handling to FCL handler
            self.fcl_handler.handle_ceid(ceid, message)
        else:
            command_logger.info(f"unknown equipment type: {
                                self.equipment_type}")

    def s09f1(self, handle, packet):
        command_logger.error(f"{self.equipment_name}, {
            self.equipment_type}, s09f1:Unrecognized Device ID (UDN)")

    def s09f3(self, handle, packet):
        command_logger.error(f"{self.equipment_name}, {
            self.equipment_type}, s09f3:Unrecognized Stream Function (SFCD)")

    def s09f5(self, handle, packet):
        command_logger.error(f"{self.equipment_name}, {
            self.equipment_type}, s09f5:Unrecognized Function Type (UFN)")

    def s09f7(self, handle, packet):
        command_logger.error(f"{self.equipment_name}, {
            self.equipment_type}, s09f7:Illegal Data (IDN)")

    def s09f9(self, handle, packet):
        command_logger.error(f"{self.equipment_name}, {
            self.equipment_type}, s09f9:Transaction Timer Timeout (TTN)")

    def s09f11(self, handle, packet):
        command_logger.error(f"{self.equipment_name}, {
            self.equipment_type}, s09f11:Data Too Long (DLN)")

    def is_enabled(self):
        return self._enabled

    def go_online(self):
        result = super().go_online()
        return result

    def go_offline(self):
        result = super().go_offline()
        return result

    def enable(self):
        super().enable()
        self._enabled = True
        # self.mqtt_client.publish(
        #     f"response/{self.equipment_name}", json.dumps({"status": "enabled"}))

    def disable(self):
        super().disable()
        self._enabled = False
        # self.mqtt_client.publish(
        #     f"response/{self.equipment_name}", json.dumps({"status": "disabled"}))

    def mqtt_control(self, command):
        """Handle MQTT commands."""
        if command == "enable":
            self.enable()
            command_logger.info(f"{self.equipment_name} enabled via MQTT.")
        elif command == "disable":
            self.disable()
            command_logger.info(f"{self.equipment_name} disabled via MQTT.")
        elif command == "go_online":
            result = self.go_online()
            if result == 0:
                command_logger.info(
                    f"{self.equipment_name} is now online via MQTT.")
            elif result == 1:
                command_logger.error(
                    f"{self.equipment_name} was refused to go online via MQTT.")
            elif result == 2:
                command_logger.warning(
                    f"{self.equipment_name} is already online via MQTT.")
            else:
                command_logger.error(f"Unknown result from go_online for {
                                     self.equipment_name}.")
        elif command == "go_offline":
            result = self.go_offline()
            if result == 0:
                command_logger.info(
                    f"{self.equipment_name} is now offline via MQTT.")
            elif result == 1:
                command_logger.error(
                    f"{self.equipment_name} was refused to go offline via MQTT.")
            elif result == 2:
                command_logger.warning(
                    f"{self.equipment_name} is already offline via MQTT.")
            else:
                command_logger.error(f"Unknown result from go_offline for {
                                     self.equipment_name}.")
        else:
            command_logger.error(f"Invalid command: {command}")


class HostCmd(cmd.Cmd):
    prompt = "> "

    def __init__(self, equipment_list, mqtt_client):
        super().__init__()
        self.equipment_list = equipment_list
        self.mqtt_client = mqtt_client

    def do_help(self, arg):
        "Show available commands."
        print("Commands:")
        print("  help - Show this message")
        print("  list - List all equipment and status")
        print("  quit - Disable equipment and exit")
        print("  enable <equipment_name> - Enable equipment")
        print("  disable <equipment_name> - Disable equipment")
        print("  go_online <equipment_name> - Set equipment online")
        print("  go_offline <equipment_name> - Set equipment offline")
        print("  add <equipment_name> <equipment_type> <address> <port> <session_id> <connect_mode> <device_type> - Add a new equipment")
        print("  delete <equipment_name> - Delete an existing equipment")
        print("  edit <equipment_name> <field> <new_value> - Edit an existing equipment")

    def emptyline(self):
        pass

    def do_list(self, arg):
        "List all equipment and status."
        command_logger.info("Equipment List:")
        for eq in self.equipment_list:
            status = "Enabled" if eq.is_enabled() else "Disabled"
            command_logger.info(
                f"  {eq.equipment_name} ({eq.equipment_type}): {status}")

    def do_quit(self, arg):
        "Disable all equipment and exit."
        self.save_config()
        for eq in self.equipment_list:
            if eq.is_enabled():
                eq.disable()
        command_logger.info("All equipment disabled. Exiting.")
        return True

    def do_enable(self, arg):
        "Enable equipment."
        equipment_name = arg.strip()
        for eq in self.equipment_list:
            if eq.equipment_name == equipment_name:
                if eq.is_enabled():
                    command_logger.info(
                        f"Equipment '{equipment_name}' is already enabled.")
                else:
                    eq.enable()
                    command_logger.info(
                        f"Equipment '{equipment_name}' is now enabled.")
                break
        else:
            command_logger.info(f"Equipment '{equipment_name}' not found.")

    def do_disable(self, arg):
        "Disable equipment."
        equipment_name = arg.strip()
        for eq in self.equipment_list:
            if eq.equipment_name == equipment_name:
                if not eq.is_enabled():
                    command_logger.info(
                        f"Equipment '{equipment_name}' is already disabled.")
                else:
                    eq.disable()
                    command_logger.info(
                        f"Equipment '{equipment_name}' is now disabled.")
                break
        else:
            command_logger.info(f"Equipment '{equipment_name}' not found.")

    def do_go_online(self, arg):
        "Set equipment online."
        equipment_name = arg.strip()
        for eq in self.equipment_list:
            if eq.equipment_name == equipment_name:
                result = eq.go_online()
                if result == 0:
                    command_logger.info(
                        f"Equipment '{equipment_name}' is now online.")
                elif result == 1:
                    command_logger.error(
                        f"Equipment '{equipment_name}' was refused to go online.")
                elif result == 2:
                    command_logger.warning(
                        f"Equipment '{equipment_name}' is already online.")
                else:
                    command_logger.error(f"Unknown result from go_online for equipment '{
                                         equipment_name}'.")
                break
        else:
            command_logger.info(f"Equipment '{equipment_name}' not found.")

    def do_go_offline(self, arg):
        "Set equipment offline."
        equipment_name = arg.strip()
        for eq in self.equipment_list:
            if eq.equipment_name == equipment_name:
                result = eq.go_offline()
                if result == 0:
                    command_logger.info(
                        f"Equipment '{equipment_name}' is now offline.")
                elif result == 1:
                    command_logger.error(
                        f"Equipment '{equipment_name}' was refused to go offline.")
                elif result == 2:
                    command_logger.warning(
                        f"Equipment '{equipment_name}' is already offline.")
                else:
                    command_logger.error(f"Unknown result from go_offline for equipment '{
                                         equipment_name}'.")
                break
        else:
            command_logger.info(f"Equipment '{equipment_name}' not found.")

    def save_config(self):
        """Save the current equipment configuration to a JSON file."""
        try:
            config = {"equipment": []}
            for eq in self.equipment_list:
                config['equipment'].append({
                    "equipment_name": eq.equipment_name,
                    "equipment_type": eq.equipment_type,
                    "address": eq.settings.address,
                    "port": eq.settings.port,
                    "session_id": eq.settings.session_id,
                    "connect_mode": eq.settings.connect_mode.name,  # Use .name for enums
                    "device_type": eq.settings.device_type.name,  # Use .name for enums
                    "enable": eq.is_enabled()
                })

            # Overwrite the config file safely
            with open('config.json', 'w', encoding='utf8') as config_file:
                json.dump(config, config_file, indent=4)

            command_logger.info("Configuration saved successfully.")

        except (IOError, TypeError, ValueError) as e:
            command_logger.error(f"Failed to save configuration: {e}")

    def do_add(self, arg):
        """
        Add a new machine or equipment to the system and save to the config file.
        Usage: add <equipment_name> <equipment_type> <address> <port> <session_id> <connect_mode> <device_type>
        """
        try:
            args = arg.split()
            if len(args) != 7:
                command_logger.error(
                    "Invalid arguments. Usage: add <equipment_name> <equipment_type> <address> <port> <session_id> <connect_mode> <device_type>")
                return

            equipment_name, equipment_type, address, port, session_id, connect_mode, device_type = args

            # Validate equipment_name (ensure it's not empty)
            if not equipment_name:
                command_logger.error("Equipment name cannot be empty.")
                return

            # Validate equipment_type (ensure it's not empty)
            if not equipment_type:
                command_logger.error("Equipment type cannot be empty.")
                return

            # Validate address (check if it's a valid IP address)
            try:
                # This will raise an exception if the address is invalid
                socket.inet_aton(address)
            except socket.error:
                command_logger.error(f"Invalid IP address: {
                                     address}. Please provide a valid address.")
                return

            # Validate port (ensure it's a valid integer and within the range)
            try:
                port = int(port)
                if port < 1 or port > 65535:
                    raise ValueError("Port must be between 1 and 65535.")
            except ValueError:
                command_logger.error(
                    f"Invalid port: {port}. Please provide a valid port number (1-65535).")
                return

            # Validate session_id (ensure it's a valid integer)
            try:
                session_id = int(session_id)
            except ValueError:
                command_logger.error(f"Invalid session_id: {
                                     session_id}. Please provide a valid integer.")
                return

            # Validate connect_mode (ensure it's a valid connect mode enum)
            valid_connect_modes = [
                mode.name for mode in secsgem.hsms.HsmsConnectMode]
            if connect_mode not in valid_connect_modes:
                command_logger.error(
                    f"Invalid connect_mode: {connect_mode}. Allowed values are: {
                        ', '.join(valid_connect_modes)}"
                )
                return
            connect_mode = secsgem.hsms.HsmsConnectMode[connect_mode]

            # Validate device_type (ensure it's a valid device type enum)
            valid_device_types = [
                dtype.name for dtype in secsgem.common.DeviceType]
            if device_type not in valid_device_types:
                command_logger.error(
                    f"Invalid device_type: {device_type}. Allowed values are: {
                        ', '.join(valid_device_types)}"
                )
                return
            device_type = secsgem.common.DeviceType[device_type]

            # Check if equipment already exists in the equipment list
            for eq in self.equipment_list:
                if eq.equipment_name == equipment_name:
                    command_logger.error(
                        f"Equipment {equipment_name} already exists.")
                    return

            # Create new equipment entry
            new_equipment = SampleHost(
                secsgem.hsms.HsmsSettings(
                    address=address,
                    port=port,
                    session_id=session_id,
                    connect_mode=connect_mode,
                    device_type=device_type
                ),
                equipment_name=equipment_name,
                equipment_type=equipment_type,
                mqtt_client=self.mqtt_client
            )

            # Append new equipment to the equipment list
            self.equipment_list.append(new_equipment)

            # Add the new equipment to the config.json
            with open('config.json', 'r+', encoding='utf8') as config_file:
                config = json.load(config_file)
                # Add the new equipment to the config
                config['equipment'].append({
                    "equipment_name": equipment_name,
                    "equipment_type": equipment_type,
                    "address": address,
                    "port": port,
                    "session_id": session_id,
                    "connect_mode": connect_mode.name,  # Save the name of the enum
                    "device_type": device_type.name,    # Save the name of the enum
                    "enable": False
                })

                # Overwrite the config file with the new equipment
                config_file.seek(0)
                json.dump(config, config_file, indent=4)

            command_logger.info(f"Added new equipment: {equipment_name}")
            self.save_config()

        except Exception as e:
            command_logger.error(f"Failed to add equipment: {e}")

    def do_delete(self, arg):
        """
        Delete an existing equipment.
        Usage: delete <equipment_name>
        """
        equipment_name = arg.strip()

        if not equipment_name:
            command_logger.error("Usage: delete <equipment_name>")
            return

        # Find the equipment in the equipment list
        equipment_to_delete = None
        for eq in self.equipment_list:
            if eq.equipment_name == equipment_name:
                equipment_to_delete = eq
                break

        if not equipment_to_delete:
            command_logger.error(f"Equipment '{equipment_name}' not found.")
            return

        try:
            # Disable the equipment if it's enabled
            if equipment_to_delete.is_enabled():
                equipment_to_delete.disable()
                command_logger.info(f"Equipment '{equipment_name}' disabled.")

            # Unsubscribe from the MQTT topic
            self.mqtt_client.unsubscribe(f"equipment/control/{equipment_name}")
            command_logger.info(
                f"Unsubscribed from 'equipment/control/{equipment_name}'.")

            # Remove from the equipment list
            self.equipment_list.remove(equipment_to_delete)
            command_logger.info(
                f"Equipment '{equipment_name}' removed from the list.")

            # Save the updated configuration to the config.json file
            self.save_config()

        except Exception as e:
            command_logger.error(f"Failed to delete equipment '{
                                 equipment_name}': {e}")

    def do_edit(self, arg):
        """
        Edit an existing machine's configuration and save to the config file.
        Usage: edit <equipment_name> <field> <new_value>
        """
        try:
            args = arg.split()
            if len(args) != 3:
                command_logger.error(
                    "Invalid arguments. Usage: edit <equipment_name> <field> <new_value>")
                return

            equipment_name, field, new_value = args

            # Validate equipment_name (ensure it's not empty)
            if not equipment_name:
                command_logger.error("Equipment name cannot be empty.")
                return

            # Find the equipment in the equipment list
            equipment_to_edit = None
            for eq in self.equipment_list:
                if eq.equipment_name == equipment_name:
                    equipment_to_edit = eq
                    break

            if not equipment_to_edit:
                command_logger.error(
                    f"Equipment '{equipment_name}' not found.")
                return

            # Validate and edit the specified field
            settings = equipment_to_edit.settings

            if field == "address":
                # Validate address (check if it's a valid IP address)
                try:
                    socket.inet_aton(new_value)
                    settings.address = new_value
                except socket.error:
                    command_logger.error(f"Invalid IP address: {
                                         new_value}. Please provide a valid address.")
                    return

            elif field == "port":
                # Validate port (ensure it's a valid integer and within the range)
                try:
                    new_value = int(new_value)
                    if new_value < 1 or new_value > 65535:
                        raise ValueError("Port must be between 1 and 65535.")
                    settings.port = new_value
                except ValueError:
                    command_logger.error(
                        f"Invalid port: {new_value}. Please provide a valid port number (1-65535).")
                    return

            elif field == "session_id":
                # Validate session_id (ensure it's a valid integer)
                try:
                    settings.session_id = int(new_value)
                except ValueError:
                    command_logger.error(f"Invalid session_id: {
                                         new_value}. Please provide a valid integer.")
                    return

            elif field == "connect_mode":
                # Validate connect_mode (ensure it's a valid connect mode enum)
                valid_connect_modes = [
                    mode.name for mode in secsgem.hsms.HsmsConnectMode]
                if new_value not in valid_connect_modes:
                    command_logger.error(f"Invalid connect_mode: {new_value}. Allowed values are: {
                                         ', '.join(valid_connect_modes)}")
                    return
                settings.connect_mode = secsgem.hsms.HsmsConnectMode[new_value]

            elif field == "device_type":
                # Validate device_type (ensure it's a valid device type enum)
                valid_device_types = [
                    dtype.name for dtype in secsgem.common.DeviceType]
                if new_value not in valid_device_types:
                    command_logger.error(f"Invalid device_type: {new_value}. Allowed values are: {
                                         ', '.join(valid_device_types)}")
                    return
                settings.device_type = secsgem.common.DeviceType[new_value]

            elif field == "equipment_type":
                # Update equipment_type directly
                equipment_to_edit.equipment_type = new_value
            else:
                command_logger.error(f"Invalid field: {
                                     field}. Valid fields are: address, port, session_id, connect_mode, device_type, equipment_type.")
                return

            # Save the updated configuration to the config.json file
            self.save_config()

            command_logger.info(f"Equipment '{equipment_name}' updated: {
                                field} -> {new_value}")

        except Exception as e:
            command_logger.error(f"Failed to edit equipment: {e}")


# MQTT setup

def on_connect(client, userdata, flags, rc):
    if rc == 0:  # Connection successful
        command_logger.info(f"Connected with result code {rc}")

        # Subscribe to control topics for equipment
        # Subscribe to all control messages
        client.subscribe("equipment/control/#")
        command_logger.info("Subscribed to 'equipment/control/#' topic.")

        # Publish system status on connect
        client.publish("secsgem/status", json.dumps({"status": "connected"}))
        command_logger.info("Published MQTT connection status: connected.")

        # # Request retained commands (useful for initializing states)
        # for eq in userdata:  # 'userdata' contains the equipment list
        #     control_topic = f"equipment/control/{eq.equipment_name}"
        #     # Trigger retained message
        #     client.publish(control_topic, "", retain=False)
        #     command_logger.info(f"Requested retained command for {
        #                         eq.equipment_name}")

    else:
        command_logger.error(f"Connection failed with result code {rc}")


def on_message(client, userdata, msg):
    topic_parts = msg.topic.split("/")
    if len(topic_parts) == 3:
        equipment_name = topic_parts[2]
        command = msg.payload.decode("utf-8")
        command_logger.info(f"Received command {command} for {equipment_name}")

        # Control equipment based on received command
        found = False
        for eq in userdata:
            if eq.equipment_name == equipment_name:
                eq.mqtt_control(command)
                found = True
                break

        # Handle case where equipment_name is not found
        if not found:
            command_logger.error(
                f"Equipment {equipment_name} not found in userdata.")
            # Optionally, send an MQTT response or error message
            client.publish(
                f"equipment/error/{equipment_name}", "Equipment not found")


def mqtt_setup(equipment_list):
    """Setup the MQTT client and connect."""
    mqtt_client = mqtt.Client(userdata=equipment_list)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    command_logger.info(f"MQTT Client initialized: {mqtt_client}")
    mqtt_client.connect("localhost", 1883, 60)
    return mqtt_client


if __name__ == "__main__":
    # Load configuration file
    try:
        with open('config.json', 'r', encoding='utf8') as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        command_logger.error("Configuration file 'config.json' not found.")
        exit(1)
    except json.JSONDecodeError:
        command_logger.error(
            "Error decoding 'config.json'. Please check the file format.")
        exit(1)

    # Set up logging
    commLogFileHandler = CommunicationLogFileHandler("log", "h")
    commLogFileHandler.setFormatter(
        logging.Formatter("%(asctime)s: %(message)s"))
    logging.getLogger("communication").addHandler(commLogFileHandler)
    logging.getLogger("communication").propagate = False

    logging.basicConfig(
        format='%(asctime)s %(name)s.%(funcName)s: %(message)s', level=logging.ERROR)

    equipment_list = []

    try:
        # Initialize MQTT client first
        mqtt_client = mqtt_setup(equipment_list)
        mqtt_client.loop_start()

        # Initialize all equipment based on configuration
        for equipment in config['equipment']:
            settings = secsgem.hsms.HsmsSettings(
                address=equipment['address'],
                port=equipment['port'],
                session_id=equipment['session_id'],
                connect_mode=secsgem.hsms.HsmsConnectMode[equipment['connect_mode']],
                device_type=secsgem.common.DeviceType[equipment['device_type']]
            )

            eq = SampleHost(
                settings,
                equipment_name=equipment['equipment_name'],
                equipment_type=equipment.get('equipment_type', 'unknown'),
                mqtt_client=mqtt_client  # Now mqtt_client is available
            )
            if equipment['enable']:
                eq.enable()
            equipment_list.append(eq)

        # Start command loop
        HostCmd(equipment_list, mqtt_client).cmdloop()

    finally:
        # Disable all equipment on exit
        for eq in equipment_list:
            if eq.is_enabled():  # Only disable if the equipment is enabled
                eq.disable()
        command_logger.info("Finally all equipment disabled. Exiting.")
