from dataclasses import dataclass
import json
import logging
from typing import Dict, List, TypedDict, Optional, Union
from src.utils.config.app_config import EQUIPMENTS_CONFIG_PATH, LOT_INFO_PATH, RECIPE_DIR, VALIDATE_EQUIPMENT_CONFIG_PATH, MQTT_SUBSCRIBE_TOPIC, MQTT_ENABLE


logger = logging.getLogger("app_logger")


class ValidateLot:
    """
    Class for validating lot information
    """

    def __init__(self, equipment_name: str, pp_name: str, lot_id: str):
        self.equipment_name = equipment_name
        self.pp_name = pp_name
        self.lot_id = lot_id
        self.data_lot = None
        self.data_config = None
        self.result = self._validate_lot()

    def _validate_lot(self):
        self.data_lot = self.LotInformation(self.lot_id)

        if not self.data_lot.success:
            logger.error("Error loading lot information")
            return {"status": False, "message": "Error loading lot information"}

        self.data_config = self.ValidationConfig(
            self.equipment_name, self.data_lot.field_by_name("SASSYPACKAGE"))

        if not self.data_config.data.success:
            logger.error("Error loading configuration data")
            return {"status": False, "message": self.data_config.data.success.get("message")}

        # Data from lot information
        lot_operation_code = self.data_lot.field_by_name("OPERATION_CODE")
        lot_on_operation = self.data_lot.field_by_name("ON_OPERATION")
        lot_lot_hold = self.data_lot.field_by_name("LOT_STATUS")

        # Data from configuration
        cfg_operation_code = self.data_config.data.operation_code
        cfg_on_operation = self.data_config.data.on_operation
        cfg_type_validate = self.data_config.data.type_validate
        cfg_recipe_name = self.data_config.data.recipe_name

        # Optional validation
        cfg_use_operation_code = self.data_config.data.use_operation_code
        cfg_use_on_operation = self.data_config.data.use_on_operation
        cfg_use_lot_hold = self.data_config.data.use_lot_hold

        if cfg_type_validate.upper() == "RECIPE":
            if cfg_recipe_name != self.pp_name:
                logger.error("Invalid recipe name %s", self.pp_name)
                return {"status": False, "message": "Invalid recipe name"}
        if cfg_use_operation_code:
            if cfg_operation_code != lot_operation_code:
                logger.error("Invalid operation code %s", lot_operation_code)
                return {"status": False, "message": "Invalid operation code"}
        if cfg_use_on_operation:
            if cfg_on_operation != lot_on_operation:
                logger.error("Invalid on operation %s", lot_on_operation)
                return {"status": False, "message": "Invalid on operation"}
        if cfg_use_lot_hold:
            if lot_lot_hold == "HELD" or lot_lot_hold == "HOLD":
                logger.error("Lot is on hold %s", self.lot_id)
                return {"status": False, "message": "Lot is on hold"}

        return {"status": True, "message": "Lot validated successfully"}

    class ValidationConfig:
        """Class for validating package data based on equipment configuration"""

        class PackageData(TypedDict, total=False):
            """Package data type"""
            package8digit: str
            use_operation_code: bool
            use_on_operation: bool
            use_lot_hold: bool
            selection_code: str
            data_with_selection_code: List[Dict[str, str]]

        class EquipmentData(TypedDict, total=False):
            """Equipment data type"""
            equipment_name: str
            data: List["ValidationConfig.PackageData"]

        @dataclass
        class DataConfig:
            """Configuration data class"""
            success: Dict[str, str] = None
            use_operation_code: bool = False
            use_on_operation: bool = False
            use_lot_hold: bool = False
            operation_code: str = ""
            on_operation: str = ""
            type_validate: str = ""
            recipe_name: str = ""
            product_name: str = ""

            def __post_init__(self):
                self.success = {"status": False,
                                "message": "Data not loaded yet"}

        def __init__(self, equipment_name: str, package_code: str):
            self.equipment_name = equipment_name
            self.package_code = package_code
            self.all_data = self._load_json()
            self.data = self.DataConfig()

            try:
                self._validate_package_code()
                found_equipment = self._find_equipment()

                if not found_equipment:
                    self.data.success = {"status": False,
                                         "message": "Equipment not found"}
                    return

                found_package = self._match_package(found_equipment)
                if not found_package:
                    self.data.success = {"status": False,
                                         "message": "Package code not found"}
                    return

                self._extract_package_data(found_package)

            except ValueError as e:
                self.data.success = {"status": False, "message": str(e)}

        def _load_json(self) -> Dict[str, List[EquipmentData]]:
            """Load JSON file and validate structure"""
            try:
                with open(VALIDATE_EQUIPMENT_CONFIG_PATH, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if not isinstance(data.get("data"), list):
                        logger.error("Invalid structure in dbvalidate.json")
                        # raise ValueError("Invalid structure in dbvalidate.json")
                    return data
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.error("Error loading dbvalidate.json: %s", e)

                # raise ValueError(f"Error loading dbvalidate.json: {e}") from e

        def _validate_package_code(self) -> None:
            """Check package code length"""
            if len(self.package_code.strip()) != 15:
                logger.error("Package code must be 15 characters long")
                raise ValueError("Package code must be 15 characters long")

        def _generate_selection_code(self, selection_rules: str) -> str:
            """Create selection code based on selection rules"""
            if len(selection_rules) != 4 or not set(selection_rules).issubset({'0', '1'}):
                logger.error("Selection rules must be 4 binary digits")
                # raise ValueError("Selection rules must be 4 binary digits")

            parts = [
                self.package_code[:8] if selection_rules[0] == '1' else "",
                self.package_code[11] if selection_rules[1] == '1' else "",
                self.package_code[12:14] if selection_rules[2] == '1' else "",
                self.package_code[14] if selection_rules[3] == '1' else ""
            ]
            return "".join(parts)

        def _find_equipment(self) -> Optional[EquipmentData]:
            """Find the equipment data from JSON"""
            for eq in self.all_data.get("data", []):
                if eq.get("equipment_name") == self.equipment_name:
                    return eq
            logger.error(
                "Equipment not found in configuration, equipment_name: %s", self.equipment_name)
            return None

        def _match_package(self, equipment: EquipmentData) -> Optional[PackageData]:
            """Find the package data that matches the package_code"""
            for pkg in equipment.get("data", []):
                if pkg.get("package8digit") == self.package_code[:8]:
                    return pkg
            logger.error(
                "Package code not found in configuration, package_code: %s", self.package_code)
            return None

        def _extract_package_data(self, package: PackageData) -> None:
            """Extract and validate package data"""
            self.data.use_operation_code = package.get(
                "use_operation_code", False)
            self.data.use_on_operation = package.get("use_on_operation", False)
            self.data.use_lot_hold = package.get("use_lot_hold", False)

            selection_rules = package.get("selection_code", "1111")
            try:
                expected_code = self._generate_selection_code(selection_rules)
            except ValueError as e:
                self.data.success = {"status": False,
                                     "message": f"Invalid selection rules: {e}"}
                logger.error("Invalid selection rules: %s", e)
                return

            matched_item = next(
                (item for item in package.get("data_with_selection_code", [])
                 if item.get("package_selection_code") == expected_code),
                None
            )

            if matched_item:
                self.data.operation_code = matched_item.get(
                    "operation_code", "")
                self.data.on_operation = matched_item.get("on_operation", "")
                self.data.type_validate = matched_item.get("type_validate", "")
                self.data.recipe_name = matched_item.get("recipe_name", "")
                self.data.product_name = matched_item.get("product_name", "")
                self.data.success = {"status": True,
                                     "message": "Data loaded successfully"}
            else:
                self.data.success = {
                    "status": False, "message": "No matching package selection code found. Expected code: " + expected_code}
                logger.error(
                    "No matching package selection code found. Expected code: %s", expected_code)

    class LotInformation:
        """
        Class for loading lot information from JSON
        """

        def __init__(self, lot_number: str):
            self.lot_number = lot_number
            self.success = False
            self.data = self._load_json()

        def _load_json(self) -> Dict:
            try:
                with open(LOT_INFO_PATH, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if data[0].get("Status", True):
                        self.success = True
                    else:
                        logger.error("Error loading lotdetail: %s",
                                     data[0].get("Message", "Unknown error"))
                    # Get first object's OutputLotInfo since data is wrapped in array
                    return data[0].get('OutputLotInfo', [])
            except FileNotFoundError:
                logger.error("%s not found", LOT_INFO_PATH)

                # raise FileNotFoundError("lotdetail.json not found")
            except json.JSONDecodeError:
                logger.error("Invalid JSON format in lotdetail.json")
                # raise ValueError("Invalid JSON format in lotdetail.json")

        def _find_field(self, search_key: str, search_value: str) -> Union[str, None]:
            for field in self.data:
                if field.get(search_key) == search_value:
                    return field.get('Value')
            return None

        def field_by_name(self, field_names: Union[str, List[str]]) -> Union[str, List[str], None]:
            """
            Get field value by field name
            Usage:
            field_by_name("FieldName")
            field_by_name(["FieldName1", "FieldName2"])
            """
            if isinstance(field_names, str):
                return self._find_field('FieldName', field_names)
            elif isinstance(field_names, list):
                return [self._find_field('FieldName', name) for name in field_names]
            logger.error("Invalid field_names type: %s", type(field_names))
            return None

        def field_by_desc(self, descriptions: Union[str, List[str]]) -> Union[str, List[str], None]:
            """
            Get field value by description
            Usage:
            field_by_desc("Description")
            field_by_desc(["Description1", "Description2"])
            """
            if isinstance(descriptions, str):
                return self._find_field('Description', descriptions)
            elif isinstance(descriptions, list):
                return [self._find_field('Description', desc) for desc in descriptions]
            logger.error("Invalid descriptions type: %s", type(descriptions))
            return None
