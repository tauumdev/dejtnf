import logging
from secsgem.hsms.packets import HsmsPacket
from src.equipment_manager.core.validation.lot_information import LotInformation
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.equipment_manager.equipment.equipment import Equipment

logger = logging.getLogger("app_logger")


class HandlerEventFCL:
    def __init__(self, equipment: "Equipment"):
        self.equipment = equipment

    def s06f11(self, handler, packet: HsmsPacket):
        decode = self.equipment.secs_decode(packet)

        for rpt in decode.RPT:
            if rpt:
                rptid = rpt.RPTID
                values = rpt.V
                lot_id, pp_name = values

                if rptid == 1000:
                    self._handle_validation_lot(pp_name.get(), lot_id.get())
                elif rptid == 1001:
                    self._handle_open_lot(pp_name.get(), lot_id.get())
                elif rptid == 1002:
                    self._handle_close_lot(pp_name.get(), lot_id.get())
                else:
                    logger.error(
                        "Unknown RPTID: %s", rptid.get())
                    print(f"Unknown RPT ID: {rptid.get()}")

    def _handle_validation_lot(self, pp_name: str, lot_id: str):
        """
        Handle validation lot
        """
        logger.info("Validation Lot %s %s", pp_name, lot_id)
        print("Validation Lot", pp_name, lot_id)

        if not lot_id:
            logger.error("Lot ID is required")
            print("Lot ID is required")
            return

        lot_info = LotInformation(lot_id)

        lot_data = lot_info.get_field_value(
            ["LOT PARAMETERS", "SASSYPACKAGE", "LOT_STATUS", "ON_OPERATION", "OPERATION_CODE", "PROCEDURE_CODE"])
        if lot_data.get("status"):
            lot_number = lot_data.get("data").get("LOT PARAMETERS") if lot_data.get(
                "data").get("LOT PARAMETERS") else "Not Found"
            pkg_code = lot_data.get("data").get("SASSYPACKAGE") if lot_data.get(
                "data").get("SASSYPACKAGE") else "Not Found"
            lot_status = lot_data.get("data").get("LOT_STATUS") if lot_data.get(
                "data").get("LOT_STATUS") else "Not Found"
            on_operation = lot_data.get("data").get("ON_OPERATION") if lot_data.get(
                "data").get("ON_OPERATION") else "Not Found"
            operation_code = lot_data.get("data").get("OPERATION_CODE") if lot_data.get(
                "data").get("OPERATION_CODE") else "Not Found"
            procedure_code = lot_data.get("data").get("PROCEDURE_CODE") if lot_data.get(
                "data").get("PROCEDURE_CODE") else "Not Found"

            # # print all lot data
            # print(f"Lot Number: {lot_number}")
            # print(f"Package Code: {pkg_code}")
            # print(f"Lot Status: {lot_status}")
            # print(f"On Operation: {on_operation}")
            # print(f"Operation Code: {operation_code}")
            # print(f"Procedure Code: {procedure_code}")

            # compare package code
            print("Comparing package code...")

            # accept lot
            accept_response = self.equipment.fc_control.fcl.accept_lot(lot_id)
            if accept_response.get("status") == "success":
                print(
                    f"{self.equipment.equipment_name} Lot successfully accepted: {lot_id}")
            else:
                print(
                    f"Failed to accept lot {lot_id}: {accept_response.get('message')}")
        else:
            print("Failed to retrieve package code")
            print(f"Messsage: {lot_data.get('message')}")

    def _handle_open_lot(self, pp_name: str, lot_id: str):
        """
        Handle open lot
        """
        self.equipment.lot_active = lot_id
        logger.info("Open Lot %s %s", pp_name, lot_id)

    def _handle_close_lot(self, pp_name_str, lot_id: str):
        """
        Handle close lot
        """
        self.equipment.lot_active = None
        logger.info("Close Lot %s %s", pp_name_str, lot_id)
