import argparse
from src.mqtt.mqtt_client import MQTTClient
from src.hosthandler.host_handler import HostHandler


def parse_cli():
    parser = argparse.ArgumentParser(description="SECSEGEM CLI Tool")
    parser.add_argument(
        '--connect', help="Connect to MQTT broker", action='store_true')
    parser.add_argument(
        '--status', help="Check the status of the system", action='store_true')
    args = parser.parse_args()
    return args


def handle_cli_commands():
    args = parse_cli()

    if args.connect:
        client = MQTTClient()
        client.connect("mqtt_broker_address")
        client.subscribe("your_topic")

    elif args.status:
        handler = HostHandler()
        handler.check_status()


if __name__ == "__main__":
    handle_cli_commands()
