import cmd
import json
import shlex
import secsgem
import paho.mqtt.client as mqtt
from src.gem_command import GemCommands
from src.gem_host import DejtnfHost

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

class MachineConfigCmd(cmd.Cmd):
    """
    Command-line interface for managing machine hosts.
    """
    intro = """
    MachineConfigCmd is a command-line interface (CLI) class for managing machine configurations. 
    It provides various commands to add, delete, edit, list, enable, disable, set online, and set offline machines.
    Commands:
        add <machine_name> <address> <port> <session_id> <connect_mode> <device_type> <connection> <machine_model>
            Add a new machine with the specified parameters.
        del <machine_name>
            Delete an existing machine by its name.
        edit <machine_name> <field> <new_value>
            Edit a machine's configuration. Valid fields are: address, port, session_id, connect_mode, device_type, connection, machine_model.
        list
            List all machines, their statuses, and machine models.
        conn <machine_name>
            Enable connection for a specific machine.
        dis <machine_name>
            Disable connection for a specific machine.
        online <machine_name>
            Set a machine online.
        offline <machine_name>
            Set a machine offline.
        back
            Go back to the main menu.
    """

    def do_intro(self, arg):
        """Show introduction and command usage."""
        print(self.intro)
    prompt = "(config) "

    def __init__(self, hosts, mqtt_client):
        super().__init__()
        self.hosts = hosts
        self.mqtt_client = mqtt_client

    def emptyline(self):
        pass

    def do_add(self, arg):
        """
        Add a new machine.
        Usage: add <machine_name> <address> <port> <session_id> <connect_mode> <device_type> <connection> <machine_model>
        """
        print("Adding a new machine...")
        try:
            params = arg.split()
            if len(params) != 8:
                print("Usage: add <machine_name> <address> <port> <session_id> <connect_mode> <device_type> <connection> <machine_model>")
                return

            # Extract parameters
            machine_name, address, port, session_id, connect_mode, device_type, connection, machine_model = params

            # Check if machine_name already exists
            if machine_name in self.hosts:
                print(f"Machine {machine_name} already exists.")
                return
            
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

    def do_del(self, arg):
        """
        Delete an existing machine.
        Usage: del <machine_name>
        """
        print("Deleting a machine...")
        try:
            machine_name = arg.strip()
            if not machine_name:
                print("Usage: del <machine_name>")
                return

            # Check if machine_name exists
            if machine_name not in self.hosts:
                print(f"Machine {machine_name} does not exist.")
                return

            # Disable the host if it is enabled
            host = self.hosts[machine_name]
            if host.enabled:
                host.disable_host(source="CLI")
                # print(f"Disabled host: {machine_name}")

            # Unsubscribe from the MQTT topic
            host.mqtt_client.unsubscribe(f"hosts/{machine_name}/command")
            print(f"Unsubscribed from hosts/{machine_name}/command")

            # Remove the host from the hosts dictionary
            del self.hosts[machine_name]
            # print(f"Deleted machine: {machine_name}")

            # Save the updated configuration
            save_machine_config(self.hosts)

        except Exception as e:
            print(f"Error deleting machine: {e}")
 
    def do_edit(self, arg):
        """
        Edit a machine's configuration.
        Usage: edit <machine_name> <field> <new_value>
        Fields: address, port, session_id, connect_mode, device_type, connection, machine_model
        """
        import shlex

        args = shlex.split(arg)

        if len(args) != 3:
            print("Usage: edit <machine_name> <field> <new_value>")
            return

        machine_name, field, new_value = args

        if machine_name not in self.hosts:
            print(f"Host '{machine_name}' not found.")
            return

        host = self.hosts[machine_name]
        settings = host.settings

        try:
            # Update the specified field
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

    def do_list(self, arg):
        """
        List all machines, their statuses, and machine models.
        Usage: list
        """
        if not self.hosts:
            print("No machines available. Use the 'add' command to add a new machine.")
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

            print(f"machine_name:{machine_name},status:{status}, address:{address}, port:{port}, session_id:{session_id}, connect_mode:{connect_mode}, device_type:{device_type}, connection:{connection} machine_model:{machine_model}, CommunicationState:{CommunicationState}")

    def do_conn(self, machine_name):
        """
        Enable connection for a specific machine.
        Usage: conn <machine_name>
        """
        print(f"Enabling connection for {machine_name}...")
        if machine_name not in self.hosts:
            print(f"Machine {machine_name} does not exist.")
            print("Usage: conn <machine_name>")
            return

        host = self.hosts[machine_name]
        host.enable_host()
        print(f"Connection enabled for {machine_name}")

    def do_dis(self, machine_name):
        """
        Disable connection for a specific machine.
        Usage: dis <machine_name>
        """
        print(f"Disabling connection for {machine_name}...")
        if machine_name not in self.hosts:
            print(f"Machine {machine_name} does not exist.")
            print("Usage: dis <machine_name>")
            return

        host = self.hosts[machine_name]
        host.disable_host()
        print(f"Connection disabled for {machine_name}")
 
    def do_online(self, machine_name):
        """
        Set a machine online.
        Usage: online <machine_name>
        """
        print(f"Setting {machine_name} online...")
        if machine_name not in self.hosts:
            print(f"Machine {machine_name} does not exist.")
            print("Usage: online <machine_name>")
            return

        host = self.hosts[machine_name]
        host.go_online(source="command")
        print(f"Machine {machine_name} is now online")

    def do_offline(self, machine_name):
        """
        Set a machine offline.
        Usage: offline <machine_name>
        """
        print(f"Setting {machine_name} offline...")
        if machine_name not in self.hosts:
            print(f"Machine {machine_name} does not exist.")
            print("Usage: offline <machine_name>")
            return

        host = self.hosts[machine_name]
        host.go_offline(source="command")
        print(f"Machine {machine_name} is now offline")

    def do_back(self, arg):
        """Go back to the main menu."""
        return True
    
class SecsCmd(cmd.Cmd):
    """
    Command-line interface for SECS commands.
    """
    intro = """
    SecsCmd is a command-line interface (CLI) class for managing SECS commands.
    It provides various commands to run remote commands, get process program lists, send equipment status requests, and handle equipment constant requests.
    Commands:
        rcmd <machine_name> <command>
            Run a remote command on a specific machine.
        ppdir <machine_name>
            Get the process program list (PPDIR) from a specified machine.
        estatus <machine_name> [svid1,svid2,...]
            Send an S1F3 Equipment Status Request to a machine.
        econst <machine_name> [cid1,cid2,...]
            Handle the 'equipment_constant_request' command.
          clear_events <machine_name>
        subscribe_event <machine_name> <event_id>
        send_remote_command <machine_name> <command>
        delete_process_programs <machine_name> <program_name>
        get_process_program_list <machine_name>
        enable_alarm <machine_name> <alarm_id>
        disable_alarm <machine_name> <alarm_id>
        list_alarms <machine_name> [alid1,alid2,...]
        list_enabled_alarms <machine_name>    
        back
            Go back to the main menu.
    """

    prompt = "(secs) "

    def __init__(self, hosts):
        super().__init__()
        self.hosts = hosts

    def emptyline(self):
        pass

    #status
    def do_estatus(self, arg):
        """
        Send an S1F3 Equipment Status Request to a machine.
        Usage: estatus <machine_name> [svid1,svid2,...]
        """
        try:
            args = arg.split()
            if len(args) < 1:
                print("Usage: estatus <machine_name> [svid1,svid2,...]")
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

    def do_econst(self, arg):
        """
        Handle the 'equipment_constant_request' command.
        Usage: econst <machine_name> [cid1,cid2,...]
        """
        try:
            # Split user input
            args = arg.split()
            if len(args) < 1:
                print("Usage: econst <machine_name> [cid1,cid2,...]")
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

    #control
    def do_rcmd(self, arg):
        """
        Run a remote command on a specific machine.
        Usage: rcmd <machine_name> <command>
        """
        import shlex

        try:
            args = shlex.split(arg)
            if len(args) < 2:
                print("Usage: rcmd <machine_name> <command>")
                return

            machine_name = args[0]
            command = ' '.join(args[1:])

            if machine_name not in self.hosts:
                print(f"Machine {machine_name} does not exist.")
                return

            host = self.hosts[machine_name]
            if not host.enabled:
                print(f"Machine {machine_name} is not enabled.")
                return

            # Execute the remote command
            result = host.execute_command(command)
            print(f"Command executed on {machine_name}: {command}")
            print(f"Result: {result}")

        except Exception as e:
            print(f"Error executing remote command: {e}")

    def do_clear_events(self, machine_name):
        """
        Clear collection events for a specific machine.
        Usage: clear_events <machine_name>
        """
        print(f"Clearing collection events for {machine_name}...")
        if machine_name not in self.hosts:
            print(f"Machine {machine_name} does not exist.")
            print("Usage: clear_events <machine_name>")
            return

        host = self.hosts[machine_name]
        if not host.enabled:
            print(f"Machine {machine_name} is not enabled.")
            return

        try:
            # Call the clear_collection_events method
            response = host.clear_collection_events()
            print(f"Collection events cleared for {machine_name}")
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error clearing collection events: {e}")

    def do_subscribe_event(self, arg):
        """
        Subscribe to a collection event on a specific machine.
        Usage: subscribe_event <machine_name> <event_id>
        """
        try:
            args = arg.split()
            if len(args) != 2:
                print("Usage: subscribe_event <machine_name> <event_id>")
                return

            machine_name, event_id = args
            event_id = int(event_id)

            if machine_name not in self.hosts:
                print(f"Machine {machine_name} does not exist.")
                return

            host = self.hosts[machine_name]
            if not host.enabled:
                print(f"Machine {machine_name} is not enabled.")
                return

            # Call the subscribe_collection_event method
            response = host.subscribe_collection_event(event_id)
            print(f"Subscribed to event {event_id} on {machine_name}")
            print(f"Response: {response}")

        except ValueError:
            print("Event ID must be an integer.")
        except Exception as e:
            print(f"Error subscribing to event: {e}")

    #recipe
    def do_ppdel(self, arg):
        """
        Delete process programs on a specific machine.
        Usage: ppdel <machine_name> <program_name>
        """

        try:
            args = shlex.split(arg)
            if len(args) < 2:
                print("Usage: ppdel <machine_name> <program_name>")
                return
            machine_name = args[0]
            program_name = args[1]

            if machine_name not in self.hosts:
                print(f"Machine {machine_name} does not exist.")
                return

            host = self.hosts[machine_name]
            if not host.enabled:
                print(f"Machine {machine_name} is not enabled.")
                return

            # Delete the process program
            result = host.delete_process_program(program_name)
            print(f"Process program '{program_name}' deleted on {machine_name}")
            print(f"Result: {result}")

        except Exception as e:
            print(f"Error deleting process program: {e}")

    def do_ppdir(self, machine_name):
        """
        Get the process program list from a specific machine.
        Usage: ppdir <machine_name>
        """
        print(f"Getting process program list for {machine_name}...")
        if machine_name not in self.hosts:
            print(f"Machine {machine_name} does not exist.")
            print("Usage: ppdir <machine_name>")
            return

        host = self.hosts[machine_name]
        if not host.enabled:
            print(f"Machine {machine_name} is not enabled.")
            return

        try:
            # Call the get_process_program_list method
            process_program_list = host.get_process_program_list()
            print(f"Process program list for {machine_name}: {process_program_list}")
        except Exception as e:
            print(f"Error getting process program list: {e}")

    #alarm
    def do_enable_alarm(self, arg):
        """
        Enable an alarm on a specific machine.
        Usage: enable_alarm <machine_name> <alarm_id>
        """
        try:
            args = arg.split()
            if len(args) != 2:
                print("Usage: enable_alarm <machine_name> <alarm_id>")
                return

            machine_name, alarm_id = args
            if machine_name not in self.hosts:
                print(f"Machine {machine_name} does not exist.")
                return

            host = self.hosts[machine_name]
            if not host.enabled:
                print(f"Machine {machine_name} is not enabled.")
                return

            # Enable the alarm
            host.enable_alarm(alarm_id)
            print(f"Alarm {alarm_id} enabled on {machine_name}")

        except Exception as e:
            print(f"Error enabling alarm: {e}")

    def do_disable_alarm(self, arg):
        """
        Disable an alarm on a specific machine.
        Usage: disable_alarm <machine_name> <alarm_id>
        """
        try:
            args = arg.split()
            if len(args) != 2:
                print("Usage: disable_alarm <machine_name> <alarm_id>")
                return

            machine_name, alarm_id = args
            if machine_name not in self.hosts:
                print(f"Machine {machine_name} does not exist.")
                return

            host = self.hosts[machine_name]
            if not host.enabled:
                print(f"Machine {machine_name} is not enabled.")
                return

            # Disable the alarm
            host.disable_alarm(alarm_id)
            print(f"Alarm {alarm_id} disabled on {machine_name}")

        except Exception as e:
            print(f"Error disabling alarm: {e}")

    def do_list_alarms(self, arg):
        """
        List alarms on a specific machine.
        Usage: list_alarms <machine_name> [alid1,alid2,...]
        """
        try:
            args = arg.split()
            if len(args) < 1:
                print("Usage: list_alarms <machine_name> [alid1,alid2,...]")
                return

            machine_name = args[0]
            alids = None
            if len(args) > 1:
                try:
                    alids = list(map(int, args[1].split(',')))
                except ValueError:
                    print("ALIDs must be integers separated by commas.")
                    return

            if machine_name not in self.hosts:
                print(f"Machine {machine_name} does not exist.")
                return

            host = self.hosts[machine_name]
            if not host.enabled:
                print(f"Machine {machine_name} is not enabled.")
                return

            # Call the list_alarms method
            alarms = host.list_alarms(alids)
            print(f"Alarms for {machine_name}: {alarms}")

        except ValueError:
            print("ALIDs must be integers separated by commas.")
        except Exception as e:
            print(f"Error listing alarms: {e}")

    def do_list_enabled_alarms(self, machine_name):
        """
        List enabled alarms on a specific machine.
        Usage: list_enabled_alarms <machine_name>
        """
        print(f"Listing enabled alarms for {machine_name}...")
        if machine_name not in self.hosts:
            print(f"Machine {machine_name} does not exist.")
            print("Usage: list_enabled_alarms <machine_name>")
            return

        host = self.hosts[machine_name]
        if not host.enabled:
            print(f"Machine {machine_name} is not enabled.")
            return

        try:
            # Call the list_enabled_alarms method
            enabled_alarms = host.list_enabled_alarms()
            print(f"Enabled alarms for {machine_name}: {enabled_alarms}")
        except Exception as e:
            print(f"Error listing enabled alarms: {e}")

    def do_back(self, arg):
        """Go back to the main menu."""
        return True

class MainCmd(cmd.Cmd):
    """Main command loop."""
    prompt = "(main) "

    def __init__(self, hosts, mqtt_client):
        super().__init__()
        self.hosts = hosts
        self.mqtt_client = mqtt_client

    def emptyline(self):
        pass

    def do_config(self, arg):
        """
        Enter the configuration command for the machine.

        This method initializes and starts the command loop for the MachineConfigCmd
        class, passing the hosts and MQTT client as arguments.

        Args:
            arg: The argument passed to the configuration command.
        """
        
        MachineConfigCmd(self.hosts,self.mqtt_client).cmdloop()

    def do_secs(self, arg):
        """
        Enter the SECS commands sub-command loop.

        This method initializes and starts the command loop for SECS (SEMI Equipment Communication Standard) commands.
        It creates an instance of the SecsCmd class, passing the current hosts, and then calls the cmdloop method
        to begin the interactive command session.

        Args:
            arg (str): The argument passed to the SECS command. This is typically ignored in this method.
        """
        SecsCmd(self.hosts).cmdloop()

    def do_exit(self, arg):
        """Exit the program."""
        print("Exiting...")
        exit(0)

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
            MainCmd(hosts, mqtt_client).cmdloop()

    except FileNotFoundError:
        # This should not trigger because we already handle the missing file above
        print("Configuration file 'machines_config.json' not found. Creating...")
        with open('machines_config.json', 'w') as f:
            json.dump({"hosts_settings": []}, f, indent=4)
        print("Please add a machine to the configuration.")
        hosts = {}
        MainCmd(hosts, mqtt_client).cmdloop()

    except Exception as e:
        print(f"Error initializing hosts: {e}")

    finally:
        try:
            for machine_name, host in hosts.items():
                host.disable_host()
                
                host.mqtt_client.unsubscribe(f"hosts/{machine_name}/command")
                print(f"Unsubscribed from hosts/{machine_name}/command")

            print(f"Disconnecting MQTT client for {machine_name}...")
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            print("All MQTT clients disconnected.")
        except Exception as e:
            print(f"Error during MQTT cleanup: {e}")
