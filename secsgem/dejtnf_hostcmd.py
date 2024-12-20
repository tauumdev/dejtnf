import cmd
import json
import shlex
import secsgem
import paho.mqtt.client as mqtt
from gem_host import DejtnfHost

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
    """Sub-command loop for host configuration."""
    prompt = "(hostconfig) "

    def __init__(self, hosts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hosts = hosts

    def emptyline(self):
        pass

    def do_add(self, arg):
        """Add a new machine."""
        print("Adding a new machine...")

    def do_del(self, arg):
        """Delete an existing machine."""
        print("Deleting a machine...")

    def do_edit(self, arg):
        """Edit an existing machine."""
        print("Editing a machine...")

    def do_list(self, arg):
        """List all machines."""
        if not self.hosts:
            print("No machines configured.")
        else:
            for name, host in self.hosts.items():
                print(f"{name}: {host}")

    def do_conn(self, machine_name):
        """Enable connection for a specific machine."""
        print(f"Enabling connection for {machine_name}...")

    def do_dis(self, machine_name):
        """Disable connection for a specific machine."""
        print(f"Disabling connection for {machine_name}...")

    def do_online(self, machine_name):
        """Set a machine online."""
        print(f"Setting {machine_name} online...")

    def do_offline(self, machine_name):
        """Set a machine offline."""
        print(f"Setting {machine_name} offline...")

    def do_back(self, arg):
        """Go back to the main menu."""
        return True
    
class SecsCmd(cmd.Cmd):
    """Sub-command loop for SECS commands."""
    prompt = "(secs) "

    def __init__(self, hosts, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hosts = hosts

    def emptyline(self):
        pass

    def do_send(self, arg):
        """Send a SECS command."""
        print("Sending SECS command...")

    def do_ppdir(self, arg):
        """Get the process program directory."""
        print("Getting process program directory...")

    def do_stream(self, arg):
        """Send a SECS stream function."""
        print("Sending SECS stream function...")

    def do_estatus(self, arg):
        """Request equipment status."""
        print("Requesting equipment status...")

    def do_econst(self, arg):
        """Request equipment constants."""
        print("Requesting equipment constants...")

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

    def do_machineconfig(self, arg):
        """Enter the host configuration sub-command loop."""
        MachineConfigCmd(self.hosts).cmdloop()

    def do_secs(self, arg):
        """Enter the SECS commands sub-command loop."""
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
                print(f"Disconnecting MQTT client for {machine_name}...")
                mqtt_client.loop_stop()
                mqtt_client.disconnect()
            print("All MQTT clients disconnected.")
        except Exception as e:
            print(f"Error during MQTT cleanup: {e}")


