from dataclasses import dataclass
from typing import List, Dict, Optional
import json


@dataclass
class MachineData:
    equipment_name: str
    recipe_name: str
    package15digit: str
    package8digit: str
    operation_code: str
    on_operation: str
    lot_status: str


@dataclass
class ValidationResult:
    equipment_name_valid: bool
    package_valid: bool
    operation_valid: bool
    lot_hold_valid: bool
    recipe_valid: bool
    overall_valid: bool
    error_message: Optional[str] = None


class RecipeValidation:
    def __init__(self, config_file: str = 'files/dbvalidate.json'):
        self.config_file = config_file
        self.config_data = self._load_config()

    def _load_config(self) -> Dict:
        with open(self.config_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def get_equipment_config(self, equipment_name: str) -> Optional[Dict]:
        for equipment in self.config_data.get('data', []):
            if equipment.get('equipment_name') == equipment_name:
                return equipment
        return None

    def _get_package_config(self, equipment_config: dict, package8digit: str) -> Optional[Dict]:
        for package_data in equipment_config.get('data', []):
            if package_data.get('package8digit') == package8digit:
                return package_data
        return None

    def validate_package(self, equipment_config: dict, package15digit: str, package8digit: str) -> bool:
        package_config = self._get_package_config(
            equipment_config, package8digit)
        if not package_config:
            return False

        for selection_data in package_config['data_with_selection_code']:
            if selection_data['package_selection_code'] in package15digit:
                return True
        return False

    def _validate_operation(self, package_config: dict, operation_code: str, on_operation: str) -> bool:
        if package_config['use_operation_code']:
            for selection_data in package_config['data_with_selection_code']:
                if operation_code != selection_data['operation_code']:
                    return False

        if package_config['use_on_operation']:
            for selection_data in package_config['data_with_selection_code']:
                if on_operation != selection_data['on_operation']:
                    return False
        return True

    def _validate_lot_hold(self, package_config: dict, lot_status: str) -> bool:
        if package_config.get('use_lot_hold', False):
            return lot_status != 'HOLD'
        return True

    def _validate_recipe(self, package_config: dict, recipe_name: str) -> bool:
        for selection_data in package_config['data_with_selection_code']:
            if selection_data['recipe_name'] == recipe_name:
                return True
        return False

    def validate_machine_data(self, machine_data: MachineData) -> ValidationResult:
        result = ValidationResult(
            equipment_name_valid=False,
            package_valid=False,
            operation_valid=False,
            lot_hold_valid=False,
            recipe_valid=False,
            overall_valid=False
        )

        # Validate equipment
        equipment_config = self.get_equipment_config(
            machine_data.equipment_name)
        if not equipment_config:
            result.error_message = "Equipment not found"
            return result
        result.equipment_name_valid = True

        # Get package config
        package_config = self._get_package_config(
            equipment_config, machine_data.package8digit)
        if not package_config:
            result.error_message = "Package config not found"
            return result

        # Validate package
        result.package_valid = self.validate_package(
            equipment_config,
            machine_data.package15digit,
            machine_data.package8digit
        )

        # Validate operations
        result.operation_valid = self._validate_operation(
            package_config,
            machine_data.operation_code,
            machine_data.on_operation
        )

        # Validate lot hold
        result.lot_hold_valid = self._validate_lot_hold(
            package_config,
            machine_data.lot_status
        )

        # Validate recipe
        result.recipe_valid = self._validate_recipe(
            package_config,
            machine_data.recipe_name
        )

        # Overall validation
        result.overall_valid = all([
            result.equipment_name_valid,
            result.package_valid,
            result.operation_valid,
            result.lot_hold_valid,
            result.recipe_valid
        ])

        return result
