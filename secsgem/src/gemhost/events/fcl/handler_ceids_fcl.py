from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.gemhost.equipment import Equipment


class HandlerCeidFcl:
    """
    Class for handling CEID
    """

    def __init__(self, ceid: int, equipment: 'Equipment'):
        self.equipment = equipment
        self.ceid = ceid
        self.ceid_list = {
            1: "PPChangeEvent",
            8: "Off-Line",
            9: "On-Line/Local",
            10: "On-Line/Remote",
        }

    def handle_ceid(self):
        """
        Handle CEID
        """
        if self.ceid == 1:
            self.equipment.secs_control.get_ppid()

        if self.ceid in [8, 9, 10]:
            self.equipment.control_state = self.ceid_list[self.ceid]
            self.equipment.mqtt_client.client.publish(
                f"equipments/status/control_state/{
                    self.equipment.equipment_name}",
                self.equipment.control_state, 0, retain=True
            )
