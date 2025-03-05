import React, { useState } from "react";
import {
    Box,
    TextField,
    Select,
    MenuItem,
    IconButton,
    Stack,
    FormControl,
    InputLabel,
} from "@mui/material";
import { Save, Cancel } from "@mui/icons-material";

interface EquipmentData {
    address: string;
    enable: string;
    equipment_model: string;
    equipment_name: string;
    mode: string;
    port: number;
    session_id: number;
}

interface EquipmentFormProps {
    initialData: EquipmentData;
    onSave: (data: EquipmentData) => void;
    onCancel: () => void;
}

const EquipmentForm: React.FC<EquipmentFormProps> = ({ initialData, onSave, onCancel }) => {
    const [formData, setFormData] = useState<EquipmentData>(initialData);

    const handleChange = (e: React.ChangeEvent<{ name?: string; value: unknown }>) => {
        const { name, value } = e.target;
        if (name) {
            setFormData((prev) => ({ ...prev, [name]: value }));
        }
    };

    const isFormValid = () => {
        const isValidIP = (ip: string) => {
            const ipRegex = /^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)$/;
            return ipRegex.test(ip);
        };
        return (
            formData.equipment_name.trim() &&
            formData.address.trim() &&
            isValidIP(formData.address)
        );
    };

    return (
        <Box component="form"
            sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 1,
                p: 1,
                width: '100%',
                mx: 'auto',
                bgcolor: 'background.paper',
                borderRadius: 2,
                boxShadow: 3,
                overflowX: 'auto'
            }}
            noValidate
            autoComplete="off">

            <TextField size="small" label="Equipment Name" name="equipment_name" value={formData.equipment_name} onChange={handleChange} sx={{ width: 180 }} />

            <FormControl size="small" sx={{ width: 150 }}>
                <InputLabel>Model</InputLabel>
                <Select size="small" name="equipment_model" label="Model" value={formData.equipment_model} onChange={handleChange} displayEmpty>
                    <MenuItem value="FCL">FCL</MenuItem>
                    <MenuItem value="FCLX">FCLX</MenuItem>
                </Select>
            </FormControl>

            <TextField size="small" label="Address" name="address" value={formData.address} onChange={handleChange} sx={{ width: 200 }} />
            <TextField size="small" label="Port" name="port" value={formData.port} onChange={handleChange} sx={{ width: 100 }} />
            <TextField size="small" label="Session ID" name="session_id" value={formData.session_id} onChange={handleChange} sx={{ width: 100 }} />

            <FormControl size="small" sx={{ width: 150 }}>
                <InputLabel>Mode</InputLabel>
                <Select size="small" name="mode" label="Mode" value={formData.mode} onChange={handleChange} displayEmpty>
                    <MenuItem value="ACTIVE">ACTIVE</MenuItem>
                    <MenuItem value="PASSIVE">PASSIVE</MenuItem>
                </Select>
            </FormControl>

            <FormControl size="small" sx={{ width: 150 }}>
                <InputLabel>Enable</InputLabel>
                <Select size="small" name="enable" label="Enable" value={formData.enable} onChange={handleChange} displayEmpty>
                    <MenuItem value="false">False</MenuItem>
                    <MenuItem value="true">True</MenuItem>
                </Select>
            </FormControl>

            <Stack direction="row" spacing={1} alignItems="center">
                <IconButton color="primary" onClick={() => onSave(formData)} disabled={!isFormValid()}>
                    <Save />
                </IconButton>
                <IconButton color="secondary" onClick={onCancel}>
                    <Cancel />
                </IconButton>
            </Stack>
        </Box>
    );
};

export default EquipmentForm;
