import json
import logging
from dataclasses import dataclass, field
from typing import List, Optional

# Configure logger
logger = logging.getLogger("app_logger")


@dataclass
class Options:
    use_operation_code: bool
    use_on_operation: bool
    use_lot_hold: bool


@dataclass
class DataWithSelectionCode:
    package_selection_code: str
    operation_code: str
    on_operation: str
    validate_type: str
    recipe_name: str
    product_name: str
    options: Options


@dataclass
class Config:
    package8digit: str
    selection_code: str
    data_with_selection_code: List[DataWithSelectionCode]


@dataclass
class Equipment:
    equipment_name: str
    config: List[Config]


@dataclass
class EquipmentConfig:
    equipment_name: str
    package_code: str
    data_with_selection_code: Optional[DataWithSelectionCode] = None

    def __post_init__(self):
        self._load_config()

    def _load_config(self):
        """Load Equipment Configuration data from API"""
        try:
            with open("src/host/handler/lot_management/config.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self._process_config_data(data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error: {str(e)}")

    def _process_config_data(self, data):
        """Process the configuration data"""
        if data and isinstance(data, list):
            for eq in data:
                if eq["equipment_name"] == self.equipment_name:
                    self._find_matching_config(eq.get("config", []))

    def _find_matching_config(self, eq_config):
        """Find the matching configuration"""
        for config in eq_config:
            if config.get("package8digit") == self.package_code[:8]:
                self._find_matching_data(config)

    def _find_matching_data(self, config):
        """Find the matching data with selection code"""
        for data in config.get("data_with_selection_code", []):
            if data.get("package_selection_code") == self._generate_selection_code(config.get("selection_code")):
                options = Options(**data["options"])
                self.data_with_selection_code = DataWithSelectionCode(
                    package_selection_code=data["package_selection_code"],
                    operation_code=data["operation_code"],
                    on_operation=data["on_operation"],
                    validate_type=data["validate_type"],
                    recipe_name=data["recipe_name"],
                    product_name=data["product_name"],
                    options=options
                )
                # logger.info(self.data_with_selection_code)

    def _generate_selection_code(self, selection_rules: str) -> str:
        """Create selection code based on selection rules"""
        if len(selection_rules) != 4 or not set(selection_rules).issubset({'0', '1'}):
            logger.error("Selection rules must be 4 binary digits")
            return ""

        parts = [
            self.package_code[:8] if selection_rules[0] == '1' else "",
            self.package_code[11] if selection_rules[1] == '1' else "",
            self.package_code[12:14] if selection_rules[2] == '1' else "",
            self.package_code[14] if selection_rules[3] == '1' else ""
        ]
        return "".join(parts)

# if __name__ == "__main__":
#     equipment = EquipmentConfig("TNF-61", "LQFA048MSDGESDM")
#     # if equipment.data_with_selection_code:
#     print(equipment.data_with_selection_code)
#     print(equipment.data_with_selection_code.options)
