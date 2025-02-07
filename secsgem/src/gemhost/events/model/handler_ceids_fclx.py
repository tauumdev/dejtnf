from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.gemhost.equipment import Equipment


class HandlerCeidFclx:
    """
    Class for handling CEID
    """

    def __init__(self, ceid: int, equipment: 'Equipment'):
        self.equipment = equipment
        self.ceid = ceid
        self.ceid_list = {
            1: "Off-Line",
            7: "On-Line/Local",
            8: "On-Line/Remote",
        }

    def handle_ceid(self):
        """
        Handle CEID
        """
        if self.ceid == 10:
            self.equipment.secs_control.get_ppid()

        if self.ceid in [1, 7, 8]:
            self.equipment.control_state = self.ceid_list[self.ceid]

            topic = f"equipments/status/control_state/{self.equipment.equipment_name}"
            self.equipment.mqtt_client.client.publish(
                topic, self.equipment.control_state, 0, retain=True)
