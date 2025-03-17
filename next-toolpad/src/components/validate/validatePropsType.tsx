// Define a type for a 4-digit binary string
type Binary4Digit = `${0 | 1}${0 | 1}${0 | 1}${0 | 1}`;

// Custom type guard to validate if a string is a 4-digit binary
export function isBinary4Digit(code: string): code is Binary4Digit {
    return /^[01]{4}$/.test(code);
}

export interface Options {
    use_operation_code: boolean;
    use_on_operation: boolean;
    use_lot_hold: boolean;
}

export interface AllowToolId {
    position_1: string[];
    position_2: string[];
    position_3: string[];
    position_4: string[];
}

export interface DataWithSelectionCode {
    options: Options;
    package_selection_code: string;
    operation_code: string;
    on_operation: string;
    validate_type: "recipe" | "toolid";
    recipe_name: string;
    product_name: string;
    allow_tool_id: AllowToolId;
}

export interface Config {
    package8digit: string;
    selection_code: Binary4Digit; // Enforce 4-digit binary string
    data_with_selection_code: DataWithSelectionCode[];
}

export interface EquipmentConfig {
    equipment_name: string;
    config: Config[];
}


// Example usage:
const exampleConfig: EquipmentConfig = {
    equipment_name: "TNF-61",
    config: [
        {
            package8digit: "SOIC-06M",
            selection_code: "1000", // Valid 4-digit binary string
            data_with_selection_code: [
                {
                    options: {
                        use_operation_code: true,
                        use_on_operation: true,
                        use_lot_hold: true
                    },
                    package_selection_code: "SOIC-06M",
                    operation_code: "TNF",
                    on_operation: "TNF",
                    validate_type: "recipe",
                    recipe_name: "SOIC 16L",
                    product_name: "SOIC 16L",
                    allow_tool_id: {
                        position_1: [],
                        position_2: [],
                        position_3: [],
                        position_4: []
                    }
                }
            ]
        }
    ]
};

// Validation function to ensure the selection_code is valid
function validateConfig(config: EquipmentConfig): boolean {
    for (const item of config.config) {
        if (!isBinary4Digit(item.selection_code)) {
            console.error(`Invalid selection_code: ${item.selection_code}`);
            return false;
        }
    }
    return true;
}

// Validate the example config
if (validateConfig(exampleConfig)) {
    console.log("Config is valid!");
} else {
    console.log("Config is invalid!");
}