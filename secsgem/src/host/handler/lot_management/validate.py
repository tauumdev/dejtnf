import logging
from src.host.handler.lot_management.lot_infomation import LotInformation
from src.host.handler.lot_management.equipment_config import EquipmentConfig
from dataclasses import dataclass

logger = logging.getLogger("app_logger")


@dataclass
class Result:
    """Result dataclass"""
    lot_id: str
    recipe_name: str
    product_name: str


class ValidateLot:
    """Validate the lot information"""

    def __init__(self, equipment_name: str, ppid: str, lot_id: str):
        self.equipment_name = equipment_name
        self.ppid = ppid
        self.lot_id = lot_id

    def validate(self):
        """Validate"""
        lot_info = LotInformation(self.lot_id)
        if not lot_info.lot_data:
            # print("Lot data not found")
            return lot_info.message
        get_field = lot_info.get_field_value(
            ["LOT PARAMETERS", "SASSYPACKAGE", "LOT_STATUS", "ON_OPERATION", "OPERATION_CODE"])

        if not get_field.get("status"):
            # print("Failed to get field value")
            return "Failed to get field value"

        data_by_field: dict = get_field.get("data", {})
        lot_parameters = data_by_field.get("LOT PARAMETERS")
        package_code = data_by_field.get("SASSYPACKAGE")
        lot_status = data_by_field.get("LOT_STATUS")
        on_operation = data_by_field.get("ON_OPERATION")
        operation_code = data_by_field.get("OPERATION_CODE")

        if lot_parameters != self.lot_id:
            # print("Lot ID mismatch")
            print(lot_parameters, self.lot_id)
            return "Lot ID mismatch"

        if not package_code:
            # print("Package code not found")
            return "Package code not found"

        # print(lot_parameters, package_code,
        #       lot_status, on_operation, operation_code)

        equipment_config = EquipmentConfig(
            self.equipment_name, package_code)
        if not equipment_config.data_with_selection_code:
            # print("Equipment configuration not found")
            return "Equipment configuration not found"

        # print(equipment_config.data_with_selection_code)

        # validate option lot status
        if equipment_config.data_with_selection_code.options.use_lot_hold:
            # if lot_status != "RUN":
            if lot_status in ["HOLD", "HELD"]:
                # print("Lot is on hold")
                return "Lot is on hold"

        # validate option on operation
        if equipment_config.data_with_selection_code.options.use_on_operation:
            if on_operation != equipment_config.data_with_selection_code.on_operation:
                # print("On operation mismatch")
                return "On operation mismatch"

        # validate option operation code
        if equipment_config.data_with_selection_code.options.use_operation_code:
            if operation_code != equipment_config.data_with_selection_code.operation_code:
                # print("Operation code mismatch")
                return "Operation code mismatch"

        # validate recipe name
        if equipment_config.data_with_selection_code.validate_type == "recipe":
            if equipment_config.data_with_selection_code.recipe_name != self.ppid:
                # print("Recipe name mismatch")
                return "Recipe name mismatch"

        result = Result(
            lot_id=lot_parameters,
            recipe_name=equipment_config.data_with_selection_code.recipe_name,
            product_name=equipment_config.data_with_selection_code.product_name
        )
        return result

    def get_recipe_by_lotid(self):
        """Get recipe name"""
        lot_info = LotInformation(self.lot_id)
        if not lot_info.lot_data:
            return "Lot data not found"
        get_field = lot_info.get_field_value(["SASSYPACKAGE"])
        if not get_field.get("status"):
            return "Failed to get field value SAPSSYPACKAGE"
        data_by_field: dict = get_field.get("data", {})
        package_code = data_by_field.get("SASSYPACKAGE")
        if not package_code:
            return "Package code not found"
        equipment_config = EquipmentConfig(
            self.equipment_name, package_code)
        if not equipment_config.data_with_selection_code:
            return "Equipment configuration not found by package code"
        return {"recipe_name": equipment_config.data_with_selection_code.recipe_name}


# if __name__ == "__main__":
#     validate_lot = ValidateLot("TNF-61", "64L_TQFP_10x10", "PABPS1857.2")
#     result = validate_lot.validate()
#     print(result)
