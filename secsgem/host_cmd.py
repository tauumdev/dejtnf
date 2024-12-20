#host_cmd.py
import cmd
import logging
import secsgem.common
import secsgem.gem
import secsgem.hsms
import secsgem.secs
import json
import shlex
import paho.mqtt.client as mqtt
from src.gem_command import GemCommands
from src.gem_host import DejtnfHost

# Global pending hosts
pending_hosts = []

def on_mqtt_message(client, userdata, msg): 
    """
    Callback for handling received MQTT messages.
    """
    payload = msg.payload.decode("utf-8")
    topic_parts = msg.topic.split("/")

    if len(topic_parts) == 3 and topic_parts[0] == "hosts":
        machine_name = topic_parts[1]
        command = payload.lower()

        host = userdata.get(machine_name)
        if not host:
            print(f"No host found for MQTT message on {msg.topic}")
            mqtt_client.publish(f"hosts/{machine_name}/commandresponse", f"No host found for MQTT message on {msg.topic}")
            return

        if command == "online":
            host.go_online(source="MQTT")
        elif command == "offline":
            host.go_offline(source="MQTT")
        elif command == "enable":
            host.enable_host(source="MQTT")
        elif command == "disable":
            host.disable_host(source="MQTT")
        else:
            print(f"Unknown command: {command}")
            mqtt_client.publish(f"hosts/{machine_name}/commandresponse", f"Unknown command: {command}")

def on_mqtt_connect(client, userdata, flags, rc):
    """
    Callback for MQTT connection.
    Re-subscribes to all topics upon reconnect and enables pending hosts.
    """
    if rc == 0:
        print("Connected to MQTT broker.")
        
        # Re-subscribe to all topics
        for machine_name, host in userdata.items():
            client.subscribe(f"hosts/{machine_name}/command")
            print(f"Subscribed to hosts/{machine_name}/command")

        # Enable hosts marked for "connection: enabled" after subscribing
        for host in pending_hosts:
            print(f"Enabling host: {host.machine_name}")
            host.enable_host()
        pending_hosts.clear()  # Clear the pending hosts list
    else:
        print(f"Failed to connect to MQTT broker. Return code: {rc}")

def save_machine_config(hosts, config_file='machines_config.json'):
    config = {"hosts_settings": []}
    for machine_name, host in hosts.items():
        settings = {
            "machine_name": machine_name,
            "address": host.settings.address,
            "port": host.settings.port,
            "session_id": host.settings.session_id,
            "connect_mode": host.settings.connect_mode.name,
            "device_type": host.settings.device_type.name,
            "connection": "enabled" if host.enabled else "disabled",
            "machine_model": host.settings.machine_model  # Include machine_model
        }
        config["hosts_settings"].append(settings)

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Configuration saved to {config_file}")

class HostCmd(cmd.Cmd):
    """
    Command-line interface for managing machine hosts.
    """
    intro = ('Type "exit" to disable hosts and exit the program.\n'
             'Type "online [machine_name]", "offline [machine_name]" to change state.\n'
             'Type "list" to show all machines and their statuses.\n'
             'Type "help <topic>" to see details of a specific command.\n')
    prompt = '(host) '

    def __init__(self, hosts, mqtt_client):
        super().__init__()
        self.hosts = hosts
        self.mqtt_client = mqtt_client

    def emptyline(self):
        pass

    def do_exit(self, arg):
        """
        Disable the hosts and exit the program.
        """
        print("Disabling hosts and exiting...")
        save_machine_config(self.hosts)  # Save config on exit

        for host in self.hosts.values():
            if host.enabled:
                host.disable_host(source="code")
        return True

    def do_online(self, arg):
        """
        Set specified host online. Usage: online [machine_name]
        """
        machine_name = arg.strip()
        if machine_name in self.hosts:
            self.hosts[machine_name].go_online(source="CLI")
        else:
            print(f"Host '{machine_name}' not found.")

    def do_offline(self, arg):
        """
        Set specified host offline. Usage: offline [machine_name]
        """
        machine_name = arg.strip()
        if machine_name in self.hosts:
            self.hosts[machine_name].go_offline(source="CLI")
        else:
            print(f"Host '{machine_name}' not found.")

    def do_list(self, arg):
        """
        List all machines, their statuses, and machine models. Usage: list
        """
        if not self.hosts:
            print("No machines available. Use the 'add_machine' command to add a new machine.")
            return
        for machine_name, host in self.hosts.items():
            status = "enabled" if host.enabled else "disabled"

            address = getattr(host.settings, 'address', 'unknown')
            port = getattr(host.settings, 'port', 'unknown')            
            session_id = getattr(host.settings, 'session_id', 'unknown')
            connect_mode = getattr(host.settings, 'connect_mode', 'unknown')
            device_type = getattr(host.settings, 'device_type', 'unknown')
            connection = status
            machine_model = getattr(host.settings, 'machine_model', 'unknown')
            CommunicationState = host._communication_state.current.name

            print(f"machine_name:{machine_name}, address:{address}, port:{port}, session_id:{session_id}, connect_mode:{connect_mode}, device_type:{device_type}, connection:{connection} machine_model:{machine_model}, CommunicationState:{CommunicationState}")

    def do_add_machine(self, arg):
        """
        Add a new machine. Usage: add_machine machine_name address port session_id connect_mode device_type connection machine_model
        """
        try:
            params = arg.split()
            if len(params) != 8:
                print("Usage: add_machine machine_name address port session_id connect_mode device_type connection machine_model")
                return

            # Extract parameters
            machine_name, address, port, session_id, connect_mode, device_type, connection, machine_model = params

            # Convert port and session_id to integers
            port = int(port)
            session_id = int(session_id)

            # Validate and convert enums
            valid_connect_modes = [mode.name for mode in secsgem.hsms.HsmsConnectMode]
            if connect_mode not in valid_connect_modes:
                print(f"Invalid connect_mode: {connect_mode}. Allowed values are: {', '.join(valid_connect_modes)}")
                return
            connect_mode = secsgem.hsms.HsmsConnectMode[connect_mode]

            valid_device_types = [dtype.name for dtype in secsgem.common.DeviceType]
            if device_type not in valid_device_types:
                print(f"Invalid device_type: {device_type}. Allowed values are: {', '.join(valid_device_types)}")
                return
            device_type = secsgem.common.DeviceType[device_type]

            # Create and configure HsmsSettings
            settings = secsgem.hsms.HsmsSettings(
                address=address,
                port=port,
                session_id=session_id,
                connect_mode=connect_mode,
                device_type=device_type
            )
            settings.machine_model = machine_model

            # Initialize DejtnfHost with mqtt_client
            host = DejtnfHost(settings, machine_name, self.mqtt_client)
            if connection.lower() == "enable":
                host.enable_host()

            self.hosts[machine_name] = host
            print(f"Added machine: {machine_name}")

            host.mqtt_client.subscribe(f"hosts/{machine_name}/command")
            print(f"Subscribed to hosts/{machine_name}/command")
            
            # Save configuration
            save_machine_config(self.hosts)

        except ValueError as e:
            print(f"Invalid value: {e}")
        except Exception as e:
            print(f"Error adding machine: {e}")

    def do_remove_machine(self, arg):
        'Remove an existing machine. Usage: remove_machine [machine_name]'
        try:
            machine_name = arg.strip()
            if machine_name in self.hosts:
                if self.hosts[machine_name].enabled:
                    self.hosts[machine_name].disable_host()  # Disable the host if it's enabled

                del self.hosts[machine_name]
                print(f"Removed machine: {machine_name}")

                # Save the updated configuration
                save_machine_config(self.hosts)
            else:
                print(f"Host '{machine_name}' not found.")

        except Exception as e:
            print(f"Error removing machine: {e}")
   
    def do_edit_machine(self, arg):
        """
        Edits a machine's configuration.
        Usage: edit_machine <machine_name> <field> <new_value>
        Fields: address, port, session_id, connect_mode, device_type, connection, machine_model
        """
        import shlex

        args = shlex.split(arg)

        if len(args) != 3:
            print("Usage: edit_machine <machine_name> <field> <new_value>")
            return

        machine_name, field, new_value = args

        if machine_name not in self.hosts:
            print(f"Host '{machine_name}' not found.")
            return

        host = self.hosts[machine_name]
        settings = host.settings

        try:
            # อัปเดตค่า field
            if field == "address":
                if hasattr(settings, "set_address"):
                    settings.set_address(new_value)
                elif hasattr(settings, "_address"):
                    settings._address = new_value
                else:
                    print("Error: Cannot update address. No setter or direct access available.")
                    return
            elif field == "port":
                if hasattr(settings, "set_port"):
                    settings.set_port(int(new_value))
                elif hasattr(settings, "_port"):
                    settings._port = int(new_value)
                else:
                    print("Error: Cannot update port. No setter or direct access available.")
                    return
            elif field == "session_id":
                if hasattr(settings, "set_session_id"):
                    settings.set_session_id(int(new_value))
                elif hasattr(settings, "_session_id"):
                    settings._session_id = int(new_value)
                else:
                    settings.session_id = int(new_value)
            elif field == "connect_mode":
                if new_value not in secsgem.hsms.HsmsConnectMode.__members__:
                    print(f"Invalid connect_mode: {new_value}. Valid values are: {list(secsgem.hsms.HsmsConnectMode.__members__.keys())}")
                    return
                if hasattr(settings, "set_connect_mode"):
                    settings.set_connect_mode(secsgem.hsms.HsmsConnectMode[new_value])
                elif hasattr(settings, "_connect_mode"):
                    settings._connect_mode = secsgem.hsms.HsmsConnectMode[new_value]
                else:
                    print("Error: Cannot update connect_mode. No setter or direct access available.")
                    return
            elif field == "device_type":
                if new_value not in secsgem.common.DeviceType.__members__:
                    print(f"Invalid device_type: {new_value}. Valid values are: {list(secsgem.common.DeviceType.__members__.keys())}")
                    return
                if hasattr(settings, "set_device_type"):
                    settings.set_device_type(secsgem.common.DeviceType[new_value])
                elif hasattr(settings, "_device_type"):
                    settings._device_type = secsgem.common.DeviceType[new_value]
                else:
                    settings.device_type = secsgem.common.DeviceType[new_value]
            elif field == "connection":
                if new_value.lower() not in ["enable", "disable"]:
                    print("Invalid connection value. Use 'enable' or 'disable'.")
                    return
                if new_value.lower() == "enable":
                    host.enable_host()
                else:
                    host.disable_host()
            elif field == "machine_model":
                if hasattr(settings, "set_machine_model"):
                    settings.set_machine_model(new_value)
                else:
                    settings.machine_model = new_value
            else:
                print(f"Invalid field: {field}. Valid fields are: address, port, session_id, connect_mode, device_type, connection, machine_model")
                return

            if field != "connection" and getattr(host, "enabled", False):
                print(f"Disabling and re-enabling connection for '{machine_name}'...")
                host.disable_host()
                host.enable_host()

            print(f"Machine '{machine_name}' updated: {field} -> {new_value}")

            save_machine_config(self.hosts)

        except ValueError as e:
            print(f"Error updating machine '{machine_name}': {e}")
        except AttributeError as e:
            print(f"Error accessing settings for '{machine_name}': {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def do_send_command(self, arg):
        '''
        Send a remote command to a host.
        Usage: send_command [machine_name] [command_name] [param1=value1] [param2=value2] ...
        '''
        try:
            # Use shlex.split to handle arguments with spaces enclosed in quotes
            params = shlex.split(arg)
            if len(params) < 2:
                print("Usage: send_command [machine_name] [command_name] [param1=value1] [param2=value2] ...")
                return

            # Extract machine name and command name from the arguments
            machine_name = params[0]
            command_name = params[1]
            param_pairs = params[2:]

            # Check if the specified machine exists in the list of hosts
            if machine_name not in self.hosts:
                print(f"Host '{machine_name}' not found.")
                return

            # Parse parameters into a list of (key, value) tuples
            param_list = []
            for pair in param_pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)  # Split into key and value
                    param_list.append((key, value))
                else:
                    # Invalid parameter format, exit early
                    print(f"Invalid parameter format: {pair}")
                    return

            # Debug print to show the command being sent
            print(f"Sending command to {machine_name}: {command_name} with params {param_list}")

            # Get the host object and check if it's enabled
            host = self.hosts[machine_name]
            if not host.enabled:
                print(f"Host '{machine_name}' is not enabled. Please enable it first.")
                return

            # Send the command to the remote host
            response = host.send_remote_command(command_name, param_list)

            # Define response codes for better readability
            RESPONSE_CODES = {
                0x0: "ok, completed",
                0x1: "invalid command",
                0x2: "cannot do now",
                0x3: "parameter error",
                0x4: "initiated for asynchronous completion",
                0x5: "rejected, already in desired condition",
                0x6: "invalid object"
            }

            # Check the response for validity and extract the response code
            if hasattr(response, "data") and len(response.data) > 0:
                response_code = response.data[0].get()  # Adjust as per the actual API structure
                # Map response code to human-readable status
                status = RESPONSE_CODES.get(response_code, f"Unknown code: {response_code}")
                print(f"Command response: {status}")
            else:
                print("Unexpected response format or missing data.")

        except Exception as e:
            # Catch and display any errors during execution
            print(f"Error sending command: {e}")
    
    def do_get_ppdir(self, arg):
        """
        Get the process program list (PPDIR) from a specified machine.
        Usage: get_ppdir [machine_name]
        """
        try:
            # Parse the machine name from the command argument
            machine_name = arg.strip()
            if not machine_name:
                print("Usage: get_ppdir [machine_name]")
                return

            # Ensure the machine exists
            if machine_name not in self.hosts:
                print(f"Host '{machine_name}' not found.")
                return
            
            # Retrieve the host object
            host = self.hosts[machine_name]
            if not host.enabled:
                print(f"Host '{machine_name}' is not enabled. Please enable it first.")
                return
            
            program_list = host.get_process_program_list()

            # Print the result
            print(f"Process Program List (PPDIR) for '{machine_name}':")
            if program_list:
                for program in program_list:
                    print(f"  - {program}")
            else:
                print("No process programs found.")
            
        except Exception as e:
            # Handle and log any errors
            print(f"Failed to get process program list for '{machine_name}': {e}")

    def do_send_stream_function(self, arg):
        """
        Send a GEM stream function command.
        Usage: send_stream_function [stream] [function] [machine_name] [key1=value1] [key2=value2] ...
        """
        try:
            # Split the input arguments
            args = arg.split()
            if len(args) < 3:
                print("Usage: send_stream_function [stream] [function] [machine_name] [key1=value1] [key2=value2] ...")
                return

            # Extract stream, function, and machine_name
            stream = int(args[0][1:])  # Strip 's' from the stream (e.g., 's1' -> 1)
            function = int(args[1][1:])  # Strip 'f' from the function (e.g., 'f19' -> 19)
            machine_name = args[2]

            # Ensure the machine exists
            if machine_name not in self.hosts:
                print(f"Host '{machine_name}' not found.")
                return

            # Parse optional key=value parameters
            param_pairs = args[3:]
            params = {}
            for pair in param_pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    params[key] = value
                else:
                    print(f"Invalid parameter format: {pair}")
                    return

            # Get the host and ensure it's enabled
            host = self.hosts[machine_name]
            if not host.enabled:
                print(f"Host '{machine_name}' is not enabled. Please enable it first.")
                return

            # Send the stream function command
            response = host.send_stream_function(stream=stream, function=function, params=params)

            # Print the response
            print(f"Response from stream {stream}, function {function} on '{machine_name}':")
            print(response)

        except ValueError:
            print("Stream and function must be valid integers prefixed with 's' and 'f', respectively.")
        except Exception as e:
            print(f"Failed to send stream function: {e}")

    def do_equipment_status_request(self, arg):
            """
            Send an S1F3 Equipment Status Request to a machine.
            Usage: equipment_status_request [machine_name] [svid1,svid2,...]
            """
            try:
                args = arg.split()
                if len(args) < 1:
                    print("Usage: equipment_status_request [machine_name] [svid1,svid2,...]")
                    return

                # Extract machine name
                machine_name = args[0]

                # Check if machine exists
                if machine_name not in self.hosts:
                    print(f"Host '{machine_name}' not found.")
                    return

                # Parse SVIDs (if provided)
                svids = []
                if len(args) > 1:
                    try:
                        svids = [int(svid) for svid in args[1].split(",")]
                    except ValueError:
                        print("SVIDs must be a comma-separated list of integers.")
                        return

                # Get the host and ensure it's enabled
                host = self.hosts[machine_name]
                if not host.enabled:
                    print(f"Host '{machine_name}' is not enabled. Please enable it first.")
                    return

                # Call send_equipment_status_request from GemCommands
                response = GemCommands.send_equipment_status_request(host, svids)

                # Print the response
                print(f"Response from S1F3 on '{machine_name}':")
                print(response)

            except Exception as e:
                print(f"Failed to send equipment status request: {e}")

    def do_equipment_constant_request(self, arg):
        """
        Handle the 'equipment_constant_request' command.
        Usage: equipment_constant_request [machine_name] [cid1,cid2,...]
        """
        try:
            # Split user input
            args = arg.split()
            if len(args) < 1:
                print("Usage: equipment_constant_request [machine_name] [cid1,cid2,...]")
                return

            # Extract machine_name and CIDs
            machine_name = args[0]
            cids = None
            if len(args) > 1:
                cids = list(map(int, args[1].split(',')))

            # Validate host existence
            if machine_name not in self.hosts:
                print(f"Host '{machine_name}' not found.")
                return

            # Execute the command
            host = self.hosts[machine_name]
            response = GemCommands.send_equipment_constant_request(host, cids)

            # Print the response
            print(f"Response from S2F13 on '{machine_name}':")
            print(response)

        except ValueError:
            print("CIDs must be integers separated by commas.")
        except Exception as e:
            print(f"Error executing equipment_constant_request: {e}")

    def do_EOF(self, line):
        'Exit the program.'
        print("Exiting...")
        save_machine_config(self.hosts)  # Save config on exit

        for host in self.hosts.values():
            if host.enabled:
                host.disable_host()
        return True

if __name__ == "__main__":
    try:
        print("Loading configuration...")
        try:
            with open('machines_config.json', 'r') as f:
                config = json.load(f)
        except FileNotFoundError:
            print("Configuration file 'machines_config.json' not found. Creating a new file...")
            # Create an empty configuration
            config = {"hosts_settings": []}
            with open('machines_config.json', 'w') as f:
                json.dump(config, f, indent=4)

        hosts_settings = config.get("hosts_settings", [])
        hosts = {}

        print("Setting up MQTT client...")
        mqtt_client = mqtt.Client()
        mqtt_client.user_data_set(hosts)
        mqtt_client.on_message = on_mqtt_message
        mqtt_client.on_connect = on_mqtt_connect

        print("Initializing hosts...")
        pending_hosts = []  # Hosts to enable after MQTT connects

        for host_settings in hosts_settings:
            settings = secsgem.hsms.HsmsSettings(
                address=host_settings["address"],
                port=host_settings["port"],
                session_id=host_settings["session_id"],
                connect_mode=secsgem.hsms.HsmsConnectMode[host_settings["connect_mode"]],
                device_type=secsgem.common.DeviceType[host_settings["device_type"]]
            )
            settings.machine_model = host_settings.get("machine_model", "unknown")

            host = DejtnfHost(settings, host_settings["machine_name"], mqtt_client)
            hosts[host_settings["machine_name"]] = host

            # Queue hosts to be enabled after MQTT connection
            if host_settings["connection"] == "enabled":
                pending_hosts.append(host)

        print("Connecting to MQTT broker...")
        mqtt_client.connect("localhost", 1883, 60)
        mqtt_client.loop_start()

        print("All systems initialized. Entering command loop.")
        HostCmd(hosts, mqtt_client).cmdloop()

    except FileNotFoundError:
        # This should not trigger because we already handle the missing file above
        print("Configuration file 'machines_config.json' not found. Creating...")
        with open('machines_config.json', 'w') as f:
            json.dump({"hosts_settings": []}, f, indent=4)
        print("Please add a machine to the configuration.")
        hosts = {}
        HostCmd(hosts, mqtt_client).cmdloop()

    except Exception as e:
        print(f"Error initializing hosts: {e}")

    finally:
        try:
            for machine_name, host in hosts.items():
                print(f"Disconnecting MQTT client for {machine_name}...")
                mqtt_client.loop_stop()
                mqtt_client.disconnect()
            print("All MQTT clients disconnected.")
        except Exception as e:
            print(f"Error during MQTT cleanup: {e}")
