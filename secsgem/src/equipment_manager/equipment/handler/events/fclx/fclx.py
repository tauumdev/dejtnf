import logging
from secsgem.hsms.packets import HsmsPacket
from typing import TYPE_CHECKING

from src.equipment_manager.core.validation.recipe_validate import MachineData, RecipeValidation
from src.equipment_manager.core.validation.lot_info import LotInformation

if TYPE_CHECKING:
    from src.equipment_manager.equipment.equipment import Equipment

logger = logging.getLogger("app_logger")


class HandlerEventFCLX:
    """
    Class to handle FCLX events
    """

    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment

    def s06f11(self, handler, packet: HsmsPacket):
        """
        Handle base on events
        """
        try:
            decode = self.equipment.secs_decode(packet)
            ceid = decode.CEID
            if ceid == 1:
                self.handle_fclx_initial()
            for rpt in decode.RPT:
                if rpt:
                    rptid = rpt.RPTID
                    values = rpt.V
                    lot_id, pp_name = values

                    lot_id = lot_id.get().strip().upper()
                    pp_name = pp_name.get().strip()

                    try:
                        if rptid == 1000:
                            if lot_id.split(",")[1] == "RECIPE":
                                print("Equipment request Recipe")
                            self._handle_validation_lot(
                                pp_name, lot_id)
                        elif rptid == 1001:
                            self._handle_open_lot(
                                pp_name, lot_id)
                        elif rptid == 1002:
                            self._handle_close_lot(
                                pp_name, lot_id)
                        else:
                            logger.error(
                                "Unknown RPTID: %s", rptid)
                            print(f"Unknown RPT ID: {rptid}")
                    except Exception as e:
                        logger.error("Error handling FCL event: %s", e)
        except Exception as e:
            logger.error("Error handling FCL event: %s", e)

    def handle_fclx_initial(self):
        """
        Handle FCLX init
        """
        logger.info("FCLX init")
        s1f4 = self.equipment.send_and_waitfor_response(
            self.equipment.stream_function(1, 3)([7]))

        decode_s1f4 = self.equipment.secs_decode(s1f4)
        self.equipment.pp_name = decode_s1f4[0].get()
        self.equipment.mqtt_client.client.publish(
            f"equipments/status/pp_name/{self.equipment.equipment_name}", self.equipment.pp_name)

    def _handle_validation_lot(self, pp_name: str, lot_id: str):
        """
        Handle validation lot
        """
        logger.info("%s Request validation Lot pp name=%s lot id=%s",
                    self.equipment.equipment_name, pp_name, lot_id)

        if not lot_id:
            logger.warning("Ignore validate lot %s %s %s: Lot id is empty",
                           self.equipment.equipment_name, pp_name, lot_id)
            return

        lot_info = LotInformation(lot_id)

        lot_data = lot_info.get_field_value(
            [
                "LOT PARAMETERS", "SASSYPACKAGE", "LOT_STATUS",
                "ON_OPERATION", "OPERATION_CODE", "PROCEDURE_CODE"
            ])

        if lot_data.get("status"):
            lot_id_info = lot_data.get("data").get("LOT PARAMETERS") if lot_data.get(
                "data").get("LOT PARAMETERS") else "Not Found"
            package_code = lot_data.get("data").get("SASSYPACKAGE") if lot_data.get(
                "data").get("SASSYPACKAGE") else "Not Found"
            lot_status = lot_data.get("data").get("LOT_STATUS") if lot_data.get(
                "data").get("LOT_STATUS") else "Not Found"
            on_operation = lot_data.get("data").get("ON_OPERATION") if lot_data.get(
                "data").get("ON_OPERATION") else "Not Found"
            operation_code = lot_data.get("data").get("OPERATION_CODE") if lot_data.get(
                "data").get("OPERATION_CODE") else "Not Found"

            #  check is not correct lot id
            if lot_id != lot_id_info:
                self.equipment.fc_control.fcl.reject_lot(
                    lot_id)
                # all logger add machine name and recipe name and lot id and message
                logger.warning("%s Reject lot %s: Lot id is incorrect",
                               self.equipment.equipment_name, lot_id)
                return

            # validate
            # logger.info("%s Validating lot %s", self.
            #             equipment.equipment_name, lot_id)
            logger.info("%s Validating lot %s: package code=%s, operation code=%s, on operation=%s, lot status=%s",
                        self.equipment.equipment_name, lot_id, package_code, operation_code, on_operation, lot_status)

            validator = RecipeValidation()
            machine_data = MachineData(
                equipment_name=self.equipment.equipment_name,
                recipe_name=pp_name,
                package15digit=package_code,
                package8digit=package_code[:8],
                operation_code=operation_code,
                on_operation=on_operation,
                lot_status=lot_status
            )

            validation_result = validator.validate_machine_data(machine_data)
            # print(validation_result)
            # logger.info("Validation result: %s", validation_result)
            logger.info("Validation result for lot %s: overall_valid=%s, error_message=%s",
                        lot_id, validation_result.overall_valid, validation_result.error_message)
            if not validation_result.overall_valid:
                logger.warning("Reason to reject lot %s: %s",
                               lot_id, validation_result.error_message or "Validation failed")

                self.equipment.fc_control.fcl.reject_lot(lot_id)
                return

            # accept lot
            self.equipment.fc_control.fcl.accept_lot(lot_id)

        else:
            logger.error("Failed to retrieve package code: %s",
                         lot_data.get("message"))

    def _handle_open_lot(self, pp_name: str, lot_id: str):
        """
        Handle open lot
        """
        self.equipment.lot_active = lot_id
        topic = f"equipments/status/lot_active/{self.equipment.equipment_name}"
        self.equipment.mqtt_client.client.publish(topic, lot_id)
        logger.info("%s Open Lot pp name=%s lot id=%s",
                    self.equipment.equipment_name, pp_name, lot_id)

    def _handle_close_lot(self, pp_name_str, lot_id: str):
        """
        Handle close lot
        """
        self.equipment.lot_active = None
        topic = f"equipments/status/lot_active/{self.equipment.equipment_name}"
        self.equipment.mqtt_client.client.publish(topic, "")
        logger.info("%s Close Lot pp name=%s lot id=%s",
                    self.equipment.equipment_name, pp_name_str, lot_id)
