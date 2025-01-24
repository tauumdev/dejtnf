import logging
import paho.mqtt.client as mqtt


logger = logging.getLogger("app_logger")


class MqttMessageHandler:
    """
    Handles incoming MQTT messages and controls equipment based on the message content.
    """

    def __init__(self, client: mqtt.Client) -> None:
        """
        Initializes the MQTT message handler.

        Args:
            client (mqtt.Client): The MQTT client instance.
        """
        self.client = client

    def on_message(self, client: mqtt.Client, eq_manager, message: mqtt.MQTTMessage) -> None:
        """
        Handles incoming MQTT messages. Parses the topic and payload to control equipment.

        Args:
            client (mqtt.Client): The MQTT client instance.
            eq_manager (EquipmentManager): The user data containing equipment manager.
            message (mqtt.MQTTMessage): The received MQTT message.
        """
        # from src.core.equipment_manager import EquipmentManager
        from src.gem.equipment_manager import EquipmentManager
        # Ensure user data is set correctly and includes "equipments"
        if not isinstance(eq_manager, EquipmentManager):
            logger.error(
                "Invalid eq_manager. Expected EquipmentManager, got %s.", type(eq_manager))
            client.publish("equipments/error/mqtt",
                           "Invalid equipment manager.")
            return

        logger.info("Message received on topic %s", message.topic)

        # Parse the topic structure
        topic_parts = message.topic.split("/")
        if len(topic_parts) == 3 and topic_parts[0] == "equipments" and topic_parts[1] == "control":
            if topic_parts[2] in ["help", "online", "offline", "enable", "disable", "rcmd"]:
                self.handler_control_command(
                    client, eq_manager, message, topic_parts)
            else:
                logger.warning("Unknown command: %s", topic_parts[2])
                client.publish("equipments/error/mqtt",
                               f"Unknown command: {topic_parts[2]}")
        elif len(topic_parts) == 3 and topic_parts[0] == "equipments" and topic_parts[1] == "config":
            if topic_parts[2] in ["help", "list"]:
                self.handler_config_command(
                    client, eq_manager, message, topic_parts)
            else:
                logger.warning("Unknown command: %s", topic_parts[2])
                client.publish("equipments/error/mqtt",
                               f"Unknown command: {topic_parts[2]}")
        else:
            logger.warning("Invalid topic format: %s", message.topic)
            client.publish("equipments/warning/mqtt",
                           f"Invalid topic format: {message.topic}")

    def help_control(self):
        _help = """
        Available commands:<control>
        Usage: equipments/control/<command>
        Commands:
            help: Display this help message
                sample
                    topic: equipments/control/help
                    payload: null
            online: Set equipment to online
                sample
                    topic: equipments/control/online 
                    payload: <equipment_name>
            offline: Set equipment to offline
                sample
                    topic: equipments/control/offline 
                    payload: <equipment_name>
            enable: Enable equipment
                sample
                    topic: equipments/control/enable
                    payload: <equipment_name>
            disable: Disable equipment
                sample
                    topic: equipments/control/disable
                    payload: <equipment_name>
        """
        return _help

    def help_config(self):
        _help = """
        Available commands:<config>
        Usage: equipments/config/<command>
        Commands:
            help: Display this help message
                sample
                    topic: equipments/config/help
                    payload: null
            list: List all equipments
                sample
                    topic: equipments/config/list
                    payload: null
        """
        return _help

    def handler_control_command(self, client: mqtt.Client, eq_manager, message: mqtt.MQTTMessage, topic_parts):

        from src.gem.equipment_manager import EquipmentManager
        # Ensure user data is set correctly and includes "equipments"
        if not isinstance(eq_manager, EquipmentManager):
            logger.error(
                "Invalid eq_manager. Expected EquipmentManager, got %s.", type(eq_manager))
            client.publish("equipments/response/error",
                           "Invalid equipment manager.")
            return

        # Parse the topic structure
        command = topic_parts[2]
        rsp_topic_control = "equipments/response/control/" + command

        if command == "help":
            help_msg = self.help_control()
            client.publish(rsp_topic_control, help_msg)
            return

        # Decode the message payload
        try:
            payload = message.payload.decode("utf-8").strip()
        except UnicodeDecodeError as e:
            logger.error("Failed to decode message payload: %s", e)
            client.publish("equipments/error/mqtt",
                           "Failed to decode message payload.")
            return

        # Determine the equipment name
        machine_name = payload

        logger.info("Processing command '%s' for equipment: %s",
                    command, machine_name)

        # Find the corresponding equipment
        equipment = next(
            (eq for eq in eq_manager.equipments if eq.equipment_name == machine_name),
            None
        )

        if equipment:
            # logger.info("Equipment found: %s", equipment.equipment_name)

            # Execute the appropriate command
            if command == "online":
                # logger.info("Set equipment '%s' to online.",
                #             equipment.equipment_name)
                rsp = eq_manager.online_equipment(machine_name)
                rsp_msg = f"Equipment {machine_name} online. response: {rsp}"
                client.publish(rsp_topic_control, rsp_msg)
            elif command == "offline":
                # logger.info("Set equipment '%s' to offline.",
                #             equipment.equipment_name)
                rsp = eq_manager.offline_equipment(machine_name)
                rsp_msg = f"Equipment {machine_name} offline. response: {rsp}"
                client.publish(rsp_topic_control, rsp_msg)
            elif command == "enable":
                # logger.info("Enabled equipment '%s'.",
                #             equipment.equipment_name)
                rsp = eq_manager.enable_equipment(machine_name)
                rsp_msg = f"Equipment {machine_name} enabled. response: {rsp}"
                client.publish(rsp_topic_control, rsp_msg)
            elif command == "disable":
                # logger.info("Disabled equipment '%s'.",
                #             equipment.equipment_name)
                rsp = eq_manager.disable_equipment(machine_name)
                rsp_msg = f"Equipment {machine_name} disabled. response: {rsp}"
                client.publish(rsp_topic_control, rsp_msg)
            elif command == "rcmd":

                rsp = eq_manager.send_remote_command(
                    machine_name, rcmd="LOT_ACCEPT", params=[["LotID", "123456"]])
                rsp_msg = f"Equipment {
                    machine_name} send remote command. response: {rsp}"
                client.publish(rsp_topic_control, rsp_msg)

        else:
            logger.warning("Equipment %s not found.", machine_name)
            client.publish("equipments/response/error",
                           f"Equipment {machine_name} not found.")

    def handler_config_command(self, client: mqtt.Client, eq_manager, message: mqtt.MQTTMessage, topic_parts):
        from src.gem.equipment_manager import EquipmentManager
        # Ensure user data is set correctly and includes "equipments"
        if not isinstance(eq_manager, EquipmentManager):
            logger.error(
                "Invalid eq_manager. Expected EquipmentManager, got %s.", type(eq_manager))
            client.publish("equipments/response/error",
                           "Invalid equipment manager.")
            return

        # Decode the message payload
        try:
            payload = message.payload.decode("utf-8").strip()
        except UnicodeDecodeError as e:
            logger.error("Failed to decode message payload: %s", e)
            client.publish("equipments/error/mqtt",
                           "Failed to decode message payload.")
            return

        # Determine the command
        command = payload.lower()
        rsp_topic_config = "equipments/response/config/" + command

        if topic_parts[2] == "help":
            help_msg = self.help_config()
            client.publish("equipments/response/config/" +
                           topic_parts[2], help_msg)
        elif topic_parts[2] == "list":
            eq_list = eq_manager.list_equipments()
            client.publish("equipments/response/config/" +
                           topic_parts[2], str(eq_list))
        else:
            logger.warning("Unknown command: %s", command)
            client.publish(rsp_topic_config, f"Unknown command. {command}")
