import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.gem.equipment_hsms import Equipment

logger = logging.getLogger("app_logger")


class HandlerAlarmFCL:
    def __init__(self, equipment: 'Equipment'):
        self.equipment = equipment

    def handle_alarm_fcl(self, ppname, lot_id, alid, alcd, altx):
        try:
            msg = json.dumps({"EquipmentName": self.equipment.equipment_name,
                              "PPName": ppname, "LotID": lot_id,
                              "ALID": alid, "ALCD": alcd, "ALTX": altx})
            logger.info("%s Alarm: %s", self.equipment.equipment_name, msg)
            self.equipment.mqtt_client.client.publish(
                f"equipments/status/alarm/{self.equipment.equipment_name}", msg, qos=1, retain=True)
            return True
        except Exception as e:
            logger.error(f"Error in handle_alarm_fcl: {e}")
            return False
