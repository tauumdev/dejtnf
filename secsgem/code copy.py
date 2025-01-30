import json
import logging
from typing import Dict, Optional
from dataclasses import dataclass
import cmd
from secsgem import GemHostHandler
import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EquipmentConfig:
    equipment_id: str
    device_id: int
    ip: str
    port: int = 5000
    mqtt_topic: Optional[str] = None


class SECSGemHost:
    """Class หลักสำหรับจัดการ Host และ Equipment ทั้งหมด"""

    def __init__(self, host: str, port: int):
        # ตั้งค่า parameters ตามที่ GemHostHandler ต้องการ
        self.handler = GemHostHandler(
            active=True,        # Host ทำงานในโหมด active
            address=(host, port),
            port=port,
            session_id=0,       # ใช้ session_id 0 สำหรับ host
            name="GEM_HOST",
            device_id=0         # ตั้งค่า device_id สำหรับ host
        )
        self._setup_callbacks()
        self.equipments: Dict[int, EquipmentConfig] = {}

    def _setup_callbacks(self):
        """ตั้งค่า Callbacks สำหรับ SECS Events"""
        self.handler.register_callback(
            self.handler.EVENT_CONNECTED, self._on_equipment_connect)
        self.handler.register_callback(
            self.handler.EVENT_DISCONNECTED, self._on_equipment_disconnect)

    def _on_equipment_connect(self, event_data):
        """Callback เมื่อมี Equipment เชื่อมต่อเข้ามา"""
        device_id = event_data["header"]["system"].device_id
        logger.info(f"Equipment {device_id} connected")

    def _on_equipment_disconnect(self, event_data):
        """Callback เมื่อ Equipment ตัดการเชื่อมต่อ"""
        device_id = event_data["header"]["system"].device_id
        logger.info(f"Equipment {device_id} disconnected")

    def send_stream_function(self, device_id: int, sf: int):
        """ส่ง Stream Function ไปยัง Equipment"""
        if device_id not in self.equipments:
            raise ValueError(f"Unknown device ID {device_id}")

        if sf == 1:
            return self.handler.send_and_wait_response(self.handler.streams_functions.s1f1())


class EquipmentManager(cmd.Cmd):
    """Manager สำหรับจัดการอุปกรณ์และ Interface"""

    prompt = "gem-host> "

    def __init__(self, mqtt_broker: str = "localhost"):
        super().__init__()
        self.gem_host = SECSGemHost("0.0.0.0", 5000)
        self.mqtt_client = mqtt.Client()
        self._setup_mqtt(mqtt_broker)

    def _setup_mqtt(self, broker: str):
        """ตั้งค่า MQTT Connection"""
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message
        self.mqtt_client.connect(broker)
        self.mqtt_client.loop_start()

    def _on_mqtt_connect(self, client, userdata, flags, rc):
        client.subscribe("gem-host/command")

    def _on_mqtt_message(self, client, userdata, msg):
        """จัดการ MQTT Messages"""
        payload = json.loads(msg.payload.decode())
        self._process_command(payload)

    def _process_command(self, command: dict):
        """ประมวลผลคำสั่งจาก MQTT/CLI"""
        action = command.get("action")

        if action == "add":
            config = EquipmentConfig(**command["config"])
            self.gem_host.equipments[config.device_id] = config
        elif action == "send_sf":
            self.gem_host.send_stream_function(
                command["device_id"],
                command["sf"]
            )

    def do_add(self, arg):
        """เพิ่ม Equipment: add <equipment_id> <device_id> <ip>"""
        args = arg.split()
        config = EquipmentConfig(
            equipment_id=args[0],
            device_id=int(args[1]),
            ip=args[2]
        )
        self.gem_host.equipments[config.device_id] = config

    def do_send_sf(self, arg):
        """ส่ง Stream Function: send_sf <device_id> <sf>"""
        device_id, sf = arg.split()
        self.gem_host.send_stream_function(int(device_id), int(sf))

    def do_list(self, arg):
        """แสดงรายการ Equipment ทั้งหมด"""
        for dev_id, config in self.gem_host.equipments.items():
            print(f"Device {dev_id}: {config.equipment_id} @ {config.ip}")


if __name__ == "__main__":
    manager = EquipmentManager()
    manager.cmdloop()
