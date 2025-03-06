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
export interface ValidateConfigPropTypes {
    _id: string;
    equipment_name: string;
    config: ConfigItem[];
}

export interface ConfigItem {
    package8digit: string;
    selection_code: string;
    data_with_selection_code: ValidateDataWithSelectionCode[];
}

export interface ValidateDataWithSelectionCode {
    options: ValidateOptions;
    package_selection_code: string;
    operation_code: string;
    on_operation: string;
    validate_type: string;
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
    position_1: any[];
    position_2: any[];
    position_3: any[];
    position_4: any[];
}

export interface ValidateResponse {
    docs: ValidateConfigPropTypes[];
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
