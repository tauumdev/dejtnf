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

// ** Config Management Functions (Add, Edit, Delete) **

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
