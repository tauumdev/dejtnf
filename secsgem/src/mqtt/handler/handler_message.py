import logging
import paho.mqtt.client as mqtt

logger = logging.getLogger("app_logger")


class HandlerMessage:
    """
    Class for handling MQTT messages
    """

    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.exist_alids: dict = {}

    def on_message(self, client, userdata, message: mqtt.MQTTMessage):
        """
        Callback function for when a PUBLISH message is received from the server.
        """
        payload = message.payload.decode("utf-8")
        topic = message.topic

        # print("Handler Mqtt Message")
        # print(f"Received message: {payload} from topic: {topic}")
        logger.info("Received message: %s from topic: %s", payload, topic)
        # self.mqtt_client.client.publish("test", "test")
        # print("Published message: test to topic: test")
        # logger.info("Published message: test to topic: test")

        if len(topic.split("/")) >= 5 and topic.split("/")[2] == "alarm":
            equipment_name = topic.split("/")[3]
            alid = topic.split("/")[4]

            if equipment_name not in self.exist_alids:
                self.exist_alids[equipment_name] = []
            if alid not in self.exist_alids[equipment_name]:
                self.exist_alids[equipment_name].append(alid)
                # print(f"Added ALID {alid} to {equipment_name}")

            # # เพิ่มหรือลบ ALID จาก exist_alids ตาม payload
            # if payload.strip():  # ถ้า payload ไม่ว่าง (Alarm เกิดขึ้น)
            #     if equipment_name not in self.exist_alids:
            #         self.exist_alids[equipment_name] = []
            #     if alid not in self.exist_alids[equipment_name]:
            #         self.exist_alids[equipment_name].append(alid)
            #         print(f"Added ALID {alid} to {equipment_name}")
            # else:  # ถ้า payload ว่าง (Alarm ถูกเคลียร์)
            #     if equipment_name in self.exist_alids:
            #         if alid in self.exist_alids[equipment_name]:
            #             self.exist_alids[equipment_name].remove(alid)
            #             print(f"Removed ALID {alid} from {equipment_name}")
            #             # ถ้าไม่มี ALID หลงเหลือให้ลบ equipment_name ออก
            #             if not self.exist_alids[equipment_name]:
            #                 del self.exist_alids[equipment_name]
            #                 print(f"Removed {equipment_name} from exist_alids")

            # # Log ข้อมูลปัจจุบันใน exist_alids
            # logger.info("Current exist_alids: %s", self.exist_alids)
            # print(f"Current exist_alids: {self.exist_alids}")
