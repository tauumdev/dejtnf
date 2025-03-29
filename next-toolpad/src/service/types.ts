export interface Equipment {
    _id: string;
    address: string;
    // createdAt: string;  
    // updatedAt: string;
    enable: boolean;
    equipment_model: string;
    equipment_name: string;
    mode: "ACTIVE" | "PASSIVE";
    port: number;
    session_id: number;
}

export interface EquipmentResponse {
    docs: Equipment[];
    hasNextPage: boolean;
    hasPrevPage: boolean;
    limit: number;
    nextPage: number | null;
    page: number;
    pagingCounter: number;
    prevPage: number | null;
    totalDocs: number;
    totalPages: number;
}

// validate interface
export interface ValidateConfig {
    // _id: string;
    equipment_name: string;
    config: ConfigItem[];
}

// Define a type for a 4-digit binary string
type Binary4Digit = `${1}${0 | 1}${0 | 1}${0 | 1}`;

// Custom type guard to validate if a string is a 4-digit binary
export function isBinary4Digit(code: string): code is Binary4Digit {
    return /^[01]{4}$/.test(code);
}

export interface ConfigItem {
    package8digit: string;
    selection_code: Binary4Digit;
    data_with_selection_code: DataWithSelectionCode[];
}

export interface DataWithSelectionCode {
    options: ValidateOptions;
    package_selection_code: string;
    operation_code: string;
    on_operation: string;
    validate_type: "recipe" | "tool_id";
    recipe_name: string;
    product_name: string;
    allow_tool_id: ValidateAllowToolId;
}

export interface ValidateOptions {
    use_operation_code: boolean;
    use_on_operation: boolean;
    use_lot_hold: boolean;
}

export interface ValidateAllowToolId {
    position_1: string[];
    position_2: string[];
    position_3: string[];
    position_4: string[];
}

export interface ValidateResponse {
    docs: ValidateConfig[];
    hasNextPage: boolean;
    hasPrevPage: boolean;
    limit: number;
    nextPage: number | null;
    page: number;
    pagingCounter: number;
    prevPage: number | null;
    totalDocs: number;
    totalPages: number;
}
