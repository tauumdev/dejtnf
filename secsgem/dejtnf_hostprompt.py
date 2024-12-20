import json
import paho.mqtt.client as mqtt
import secsgem
from src.gem_host import DejtnfHost
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError


# MQTT callbacks
def on_mqtt_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8")
    topic_parts = msg.topic.split("/")

    if len(topic_parts) == 3 and topic_parts[0] == "hosts":
        machine_name = topic_parts[1]
        command = payload.lower()

        host = userdata.get(machine_name)
        if not host:
            print(f"No host found for MQTT message on {msg.topic}")
            client.publish(
                f"hosts/{machine_name}/commandresponse",
                f"No host found for MQTT message on {msg.topic}",
            )
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
            client.publish(
                f"hosts/{machine_name}/commandresponse", f"Unknown command: {command}"
            )


def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker.")
        for machine_name, host in userdata.items():
            client.subscribe(f"hosts/{machine_name}/command")
            print(f"Subscribed to hosts/{machine_name}/command")
        for host in pending_hosts:
            print(f"Enabling host: {host.machine_name}")
            host.enable_host()
        pending_hosts.clear()
    else:
        print(f"Failed to connect to MQTT broker. Return code: {rc}")


# Save machine configuration
def save_machine_config(hosts, config_file="machines_config.json"):
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
            "machine_model": host.settings.machine_model,
        }
        config["hosts_settings"].append(settings)

    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
    print(f"Configuration saved to {config_file}")


# Sub-command loops
class MachineConfigCmd:
    def __init__(self, hosts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hosts = hosts
        self.session = PromptSession()
        self.commands = WordCompleter(
            ["add", "del", "edit", "list", "back", "help"], ignore_case=True
        )

    def run(self):
        print("Entering the machine configuration menu. Type 'help' for commands.")
        while True:
            try:
                user_input = self.session.prompt(
                    "(hostconfig) ", completer=self.commands
                )
                if not user_input:
                    continue
                if user_input.lower() == "back":
                    print("Returning to the main menu.")
                    break
                elif user_input.lower() == "help":
                    self.show_help()
                elif user_input.lower() == "list":
                    self.list_machines()
                elif user_input.lower() == "add":
                    self.add_machine()
                elif user_input.lower() == "del":
                    self.delete_machine()
                elif user_input.lower() == "edit":
                    self.edit_machine()
                else:
                    print(f"Unknown command: {user_input}")
            except KeyboardInterrupt:
                print("\nUse 'back' to return to the main menu.")
            except EOFError:
                break

    def show_help(self):
        print("\nAvailable commands:")
        print("  add    - Add a new machine")
        print("  del    - Delete an existing machine")
        print("  edit   - Edit a machine")
        print("  list   - List all machines")
        print("  back   - Return to the main menu")
        print("  help   - Show this help message\n")

    def list_machines(self):
        print("\nConfigured machines:")
        if not self.hosts:
            print("  No machines configured.")
        else:
            for name, host in self.hosts.items():
                print(f"  {name}: {host}")
        print()

    def add_machine(self):
        print("Adding a new machine...")
        # Collect inputs and add machine logic

    def delete_machine(self):
        print("Deleting a machine...")
        # Delete machine logic

    def edit_machine(self):
        print("Editing a machine...")
        # Edit machine logic


# Sub-command loops
class SecsCmd:
    """
    Sub-command loop for SECS commands.
    """

    def __init__(self, hosts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hosts = hosts
        self.session = PromptSession()
        self.commands = WordCompleter(
            ["rcmd", "ppdir", "stream", "estatus", "econst", "back", "help"],
            ignore_case=True,
        )

    def show_help(self):
        """Display help for available commands."""
        print(
            """
        Available commands:
        rcmd      - Send a SECS remote command
        ppdir     - Get the process program directory
        stream    - Send a SECS stream function
        estatus   - Request equipment status
        econst    - Request equipment constants
        back      - Return to the main menu
        help      - Show this help message
        """
        )

    def run(self):
        """
        Main loop for the SECS command interface.
        """
        print("Entering the SECS commands menu. Type 'help' for commands.")
        while True:
            try:
                user_input = self.session.prompt(
                    "(secs) ", completer=self.commands
                ).strip()
                if not user_input:  # Skip if no input
                    continue
                if user_input.lower() == "back":
                    print("Returning to the main menu.")
                    break
                elif user_input.lower() == "help":
                    self.show_help()
                elif user_input.lower() == "rcmd":
                    self.do_rcmd()
                elif user_input.lower() == "ppdir":
                    self.do_ppdir()
                elif user_input.lower() == "stream":
                    self.do_stream()
                elif user_input.lower() == "estatus":
                    self.do_estatus()
                elif user_input.lower() == "econst":
                    self.do_econst()
                else:
                    print(f"Unknown command: {user_input}")
            except KeyboardInterrupt:
                print("\nUse 'back' to return to the main menu.")
            except EOFError:
                break

    def do_rcmd(self):
        """Send a SECS command."""
        print("Sending SECS command...")

    def do_ppdir(self):
        """Get the process program directory."""
        print("Getting process program directory...")

    def do_stream(self):
        """Send a SECS stream function."""
        print("Sending SECS stream function...")

    def do_estatus(self):
        """Request equipment status."""
        print("Requesting equipment status...")

    def do_econst(self):
        """Request equipment constants."""
        print("Requesting equipment constants...")


class MainCmd:
    def __init__(self, hosts, mqtt_client):
        self.hosts = hosts
        self.mqtt_client = mqtt_client
        self.session = PromptSession()
        self.commands = WordCompleter(
            ["machineconfig", "secscommands", "exit", "help"], ignore_case=True
        )

    def run(self):
        print("Welcome to the main command loop. Type 'help' for available commands.")
        while True:
            try:
                user_input = self.session.prompt("(main) ", completer=self.commands)
                if not user_input:
                    continue
                if user_input.lower() == "exit":
                    print("Exiting...")
                    break
                elif user_input.lower() == "help":
                    self.show_help()
                elif user_input.lower() == "machineconfig":
                    self.run_machine_config()
                elif user_input.lower() == "secscommands":
                    self.run_secs_commands()
                else:
                    print(f"Unknown command: {user_input}")
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit.")
            except EOFError:
                break

    def show_help(self):
        print("\nAvailable commands:")
        print("  machineconfig  - Enter the machine configuration menu")
        print("  secscommands   - Enter the SECS commands menu")
        print("  exit           - Exit the program")
        print("  help           - Show this help message\n")

    def run_machine_config(self):
        MachineConfigCmd(self.hosts).run()

    def run_secs_commands(self):
        SecsCmd(self.hosts).run()


# Main application
if __name__ == "__main__":
    try:
        print("Loading configuration...")
        try:
            with open("machines_config.json", "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            print("Configuration file not found. Creating a new one...")
            config = {"hosts_settings": []}
            with open("machines_config.json", "w") as f:
                json.dump(config, f, indent=4)

        hosts_settings = config.get("hosts_settings", [])
        hosts = {}

        print("Setting up MQTT client...")
        mqtt_client = mqtt.Client()
        mqtt_client.user_data_set(hosts)
        mqtt_client.on_message = on_mqtt_message
        mqtt_client.on_connect = on_mqtt_connect

        print("Initializing hosts...")
        pending_hosts = []
        for host_settings in hosts_settings:
            settings = secsgem.hsms.HsmsSettings(
                address=host_settings["address"],
                port=host_settings["port"],
                session_id=host_settings["session_id"],
                connect_mode=secsgem.hsms.HsmsConnectMode[
                    host_settings["connect_mode"]
                ],
                device_type=secsgem.common.DeviceType[host_settings["device_type"]],
            )
            settings.machine_model = host_settings.get("machine_model", "unknown")
            host = DejtnfHost(settings, host_settings["machine_name"], mqtt_client)
            hosts[host_settings["machine_name"]] = host
            if host_settings["connection"] == "enabled":
                pending_hosts.append(host)

        print("Connecting to MQTT broker...")
        mqtt_client.connect("localhost", 1883, 60)
        mqtt_client.loop_start()

        print("All systems initialized. Entering command loop.")
        MainCmd(hosts, mqtt_client).run()

    except Exception as e:
        print(f"Error initializing application: {e}")

    finally:
        try:
            for machine_name, host in hosts.items():
                host.disable_host()
                print(f"Disconnecting MQTT client for {machine_name}...")
                mqtt_client.loop_stop()
                mqtt_client.disconnect()
            print("All MQTT clients disconnected.")
        except Exception as e:
            print(f"Error during MQTT cleanup: {e}")
