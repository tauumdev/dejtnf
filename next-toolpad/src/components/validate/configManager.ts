// configManager.ts

// ** Types and Interfaces **

export type Binary4Digit = `${1}${0 | 1}${0 | 1}${0 | 1}`;

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
    validate_type: "recipe" | "tool_id";
    recipe_name: string;
    product_name: string;
    allow_tool_id: AllowToolId;
}

export interface ConfigItem {
    package8digit: string;
    selection_code: Binary4Digit;
    data_with_selection_code: DataWithSelectionCode[];
}

export interface ValidateConfig {
    _id?: string | null;
    equipment_name: string;
    config: ConfigItem[];
}

// ** Validation Functions **

export function isBinary4Digit(code: string): code is Binary4Digit {
    return /^[01]{4}$/.test(code);
}

export function validateSelectionCodeLength(selectionCode: string): boolean {
    return selectionCode.length === 4 && isBinary4Digit(selectionCode);
}

// ** Config Management Functions (Add, Edit, Delete) **

export function addConfigItem(
    validateConfig: ValidateConfig,
    package8digit: string,
    selection_code: Binary4Digit,
    dataWithSelectionCode: DataWithSelectionCode
): ValidateConfig {
    // Check if the package8digit already exists
    const existingConfig = validateConfig.config.find(
        (config) => config.package8digit === package8digit
    );

    if (existingConfig) {
        // If the package8digit exists, check if the selection_code is already used
        const existingSelectionCode = existingConfig.selection_code === selection_code;

        if (existingSelectionCode) {
            throw new Error("This selection_code already exists for the given package8digit.");
        }

        // If the selection_code doesn't exist in the current config, add the new data_with_selection_code
        existingConfig.data_with_selection_code.push(dataWithSelectionCode);

        return {
            ...validateConfig,
            config: [...validateConfig.config],
        };
    } else {
        // If the package8digit doesn't exist, create a new ConfigItem
        const package_selection_code = generatePackageWithSelectionCode(package8digit + "000000000000", selection_code);

        const newConfigItem: ConfigItem = {
            package8digit,
            selection_code,
            data_with_selection_code: [dataWithSelectionCode],
        };

        return {
            ...validateConfig,
            config: [...validateConfig.config, newConfigItem],
        };
    }
}

export function editConfigItem(
    validateConfig: ValidateConfig,
    package8digit: string,
    selection_code: Binary4Digit,
    newDataWithSelectionCode: DataWithSelectionCode
): ValidateConfig {
    const configIndex = validateConfig.config.findIndex(
        (config) => config.package8digit === package8digit && config.selection_code === selection_code
    );

    if (configIndex === -1) {
        throw new Error("ConfigItem not found for the given package8digit and selection_code.");
    }

    const updatedConfig = { ...validateConfig.config[configIndex] };

    updatedConfig.data_with_selection_code = [
        ...updatedConfig.data_with_selection_code,
        newDataWithSelectionCode,
    ];

    const updatedConfigItems = [...validateConfig.config];
    updatedConfigItems[configIndex] = updatedConfig;

    return {
        ...validateConfig,
        config: updatedConfigItems,
    };
}

export function deleteConfigItem(
    validateConfig: ValidateConfig,
    package8digit: string,
    selection_code: Binary4Digit
): ValidateConfig {
    const configIndex = validateConfig.config.findIndex(
        (config) => config.package8digit === package8digit && config.selection_code === selection_code
    );

    if (configIndex === -1) {
        throw new Error("ConfigItem not found for the given package8digit and selection_code.");
    }

    const updatedConfigItems = validateConfig.config.filter(
        (config, index) => index !== configIndex
    );

    return {
        ...validateConfig,
        config: updatedConfigItems,
    };
}

// ** Utility Function: generatePackageWithSelectionCode **

export const generatePackageWithSelectionCode = (code15digit: string, selectionCode: string): string => {
    if (code15digit.length !== 15) {
        throw new Error("The 15-digit code must be exactly 15 characters long.");
    }

    const basePackage = code15digit.substring(0, 8);
    const specialMold = code15digit[11];
    const depopulatePin = code15digit.substring(12, 14);
    const plateType = code15digit[14];

    const [includeBase, includeSpecialMold, includeDepopulatePin, includePlateType] =
        selectionCode.split("").map((digit) => digit === "1");

    let result = basePackage;
    if (includeSpecialMold) result += specialMold;
    if (includeDepopulatePin) result += depopulatePin;
    if (includePlateType) result += plateType;

    return result;
};
