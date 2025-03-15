'use client'
import React, { useState } from "react";

interface EquipmentFormProps {
    initialData?: any;
    onSubmit: (data: any) => void;
}

const EquipmentForm: React.FC<EquipmentFormProps> = ({ initialData, onSubmit }) => {
    const [formData, setFormData] = useState(initialData || {
        package8digit: "",
        selection_code: "",
        data_with_selection_code: [{
            options: {
                use_operation_code: false,
                use_on_operation: false,
                use_lot_hold: false
            },
            package_selection_code: "",
            operation_code: "",
            on_operation: "",
            validate_type: "",
            recipe_name: "",
            product_name: "",
            allow_tool_id: {
                position_1: [],
                position_2: [],
                position_3: [],
                position_4: []
            }
        }]
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit(formData);
    };

    return (
        <form onSubmit={handleSubmit}>
            <label>
                Package 8 Digit:
                <input
                    type="text"
                    name="package8digit"
                    value={formData.package8digit}
                    onChange={handleChange}
                />
            </label>
            <label>
                Selection Code:
                <input
                    type="text"
                    name="selection_code"
                    value={formData.selection_code}
                    onChange={handleChange}
                />
            </label>
            <button type="submit">Save</button>
        </form>
    );
};

export default EquipmentForm;