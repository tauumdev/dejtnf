import logging
import paho.mqtt.client as mqtt


logger = logging.getLogger("config_loader")


class MqttMessageHandler:
    """
    Handles incoming MQTT messages and controls equipment based on the message content.
    """

    def on_message(self, client: mqtt.Client, eq_manager, message: mqtt.MQTTMessage) -> None:
        """
        Handles incoming MQTT messages. Parses the topic and payload to control equipment.

        Args:
            client (mqtt.Client): The MQTT client instance.
            eq_manager (EquipmentManager): The user data containing equipment manager.
            message (mqtt.MQTTMessage): The received MQTT message.
        """
        from src.core.equipment_manager import EquipmentManager
        # Ensure user data is set correctly and includes "equipments"
        if not isinstance(eq_manager, EquipmentManager):
            logger.error(
                "Invalid eq_manager. Expected EquipmentManager, got %s.", type(eq_manager))
            client.publish("equipment/response/error",
                           "Invalid equipment manager.")
            return

        logger.info("Message received on topic %s", message.topic)

        # Decode the message payload
        try:
            payload = message.payload.decode("utf-8").strip()
        except UnicodeDecodeError as e:
            logger.error("Failed to decode message payload: %s", e)
            client.publish("equipment/response/error",
                           "Failed to decode message payload.")
            return

        # Parse the topic structure
        topic_parts = message.topic.split("/")
        if len(topic_parts) == 3 and topic_parts[0] == "equipment" and topic_parts[1] == "control":

            self.handle_control_command(
                client, eq_manager, message, payload, topic_parts)

        elif len(topic_parts) == 2 and topic_parts[0] == "equipment" and topic_parts[1] == "config":

            self.handle_config_command(client, eq_manager, message, payload)

        else:
            logger.warning("Invalid topic format: %s", message.topic)
            client.publish("equipment/response/error",
                           f"Invalid topic format: {message.topic}")

    def handle_control_command(self, client: mqtt.Client, eq_manager, message, payload, topic_parts):

        from src.core.equipment_manager import EquipmentManager
        # Ensure user data is set correctly and includes "equipments"
        if not isinstance(eq_manager, EquipmentManager):
            logger.error(
                "Invalid eq_manager. Expected EquipmentManager, got %s.", type(eq_manager))
            client.publish("equipment/response/error",
                           "Invalid equipment manager.")
            return

        machine_name = topic_parts[2]
        command = payload.lower()

        # Find the corresponding equipment
        equipment = next(
            (eq for eq in eq_manager.equipments if eq.equipment_name == machine_name),
            None
        )

        if equipment:
            rsp_topic_control = "equipment/response/control/" + machine_name + "/" + command

            logger.info("Processing command '%s' for equipment: %s",
                        command, equipment.equipment_name)

            # Execute the appropriate command
            if command == "online":
                logger.info("Set equipment '%s' to online.",
                            equipment.equipment_name)
                rsp = eq_manager.online_equipment(machine_name)
                client.publish(rsp_topic_control, rsp)
            elif command == "offline":
                logger.info("Set equipment '%s' to offline.",
                            equipment.equipment_name)
                rsp = eq_manager.offline_equipment(machine_name)
                client.publish(rsp_topic_control, rsp)
            elif command == "enable":
                logger.info("Enabled equipment '%s'.",
                            equipment.equipment_name)
                rsp = eq_manager.enable_equipment(machine_name)
                client.publish(rsp_topic_control, rsp)
            elif command == "disable":
                logger.info("Disabled equipment '%s'.",
                            equipment.equipment_name)
                rsp = eq_manager.disable_equipment(machine_name)
                client.publish(rsp_topic_control, rsp)
            else:
                logger.warning("Unknown command: %s", command)
                client.publish(rsp_topic_control,
                               f"Unknown command. {command}")

        else:
            logger.warning("Equipment %s not found.", machine_name)
            client.publish(rsp_topic_control, f"Equipment {
                           machine_name} not found.")

    def handle_config_command(self, client: mqtt.Client, eq_manager, message, payload):
        from src.core.equipment_manager import EquipmentManager
        # Ensure user data is set correctly and includes "equipments"
        if not isinstance(eq_manager, EquipmentManager):
            logger.error(
                "Invalid eq_manager. Expected EquipmentManager, got %s.", type(eq_manager))
            client.publish("equipment/response/error",
                           "Invalid equipment manager.")
            return

        command = payload.lower()
        rsp_topic_config = "equipment/response/config/" + command

        # Execute the appropriate command
        if command == "list":
            list_eq = eq_manager.list_equipment()
            logger.info(list_eq)
            client.publish(rsp_topic_config, list_eq)
        else:
            logger.warning("Unknown command: %s", command)
            client.publish(rsp_topic_config, f"Unknown command. {command}")
