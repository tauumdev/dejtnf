'use client';

import {
    Box, Button, Checkbox, Dialog, DialogActions, DialogContent, DialogTitle, Divider, Grid, TextField, Typography, FormControlLabel,
    IconButton, MenuItem
} from '@mui/material';
import React, { useState } from 'react';
import { EquipmentConfig, Config, DataWithSelectionCode, Options, AllowToolId } from './validatePropsType';
import { Add } from '@mui/icons-material';

export const DialogAddValidateDataForm = ({ open, onSave, handleClose }: { open: boolean; onSave: (data: EquipmentConfig) => void; handleClose: () => void; }) => {
    // State for level 1 : Equipment Name
    const [equipmentName, setEquipmentName] = useState<string>('');

    // State for level 2 : Package Information
    const [code15digit, setCode15digit] = useState<string>('');
    const [selectionCode, setSelectionCode] = useState<"1000" | "0000" | "0001" | "0010" | "0011" | "0100" | "0101" | "0110" | "0111" | "1001" | "1010" | "1011" | "1100" | "1101" | "1110" | "1111">("1000");
    const [packageResult, setPackageResult] = useState<string>('');

    // State for level 3 : Data with Selection Code
    const [dataWithSelectionCode, setDataWithSelectionCode] = useState<DataWithSelectionCode>({
        package_selection_code: '',
        options: { use_operation_code: false, use_on_operation: false, use_lot_hold: false },
        operation_code: '',
        on_operation: '',
        validate_type: 'recipe',
        recipe_name: '',
        product_name: '',
        allow_tool_id: { position_1: [], position_2: [], position_3: [], position_4: [] }
    });

    // State for managing multiple configurations
    const [equipmentConfig, setEquipmentConfig] = useState<EquipmentConfig>({
        equipment_name: '',
        config: []
    });

    /**
    * Generates a package name based on a 15-digit input and a 4-digit selection code.
    */
    const generatePackageWithSelectionCode = (code15digit: string, selectionCode: string): string => {
        if (code15digit.length !== 15) {
            throw new Error("The 15-digit code must be exactly 15 characters long.");
        }
        if (selectionCode.length !== 4 || !/^[01]{4}$/.test(selectionCode)) {
            throw new Error("The selection code must be a 4-digit binary string (0 or 1).");
        }

        const basePackage = code15digit.substring(0, 8); // Positions 1-8
        const specialMold = code15digit[11]; // Position 12
        const depopulatePin = code15digit.substring(12, 14); // Positions 13-14
        const plateType = code15digit[14]; // Position 15

        const [includeBase, includeSpecialMold, includeDepopulatePin, includePlateType] =
            selectionCode.split("").map((digit) => digit === "1");

        let result = basePackage; // Base package is always included
        if (includeSpecialMold) result += specialMold;
        if (includeDepopulatePin) result += depopulatePin;
        if (includePlateType) result += plateType;

        return result;
    };

    // Handle changes to the 15-digit code
    const handleCode15DigitChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = event.target.value;
        setCode15digit(value);

        if (value.length === 15 && selectionCode.length === 4) {
            try {
                const result = generatePackageWithSelectionCode(value, selectionCode);
                setPackageResult(result);
            } catch (error) {
                setPackageResult("Invalid input or selection code");
            }
        } else {
            setPackageResult("");
        }
    };

    // Handle changes to the selection code
    const handleSelectionCodeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = event.target.value as "1000" | "0000" | "0001" | "0010" | "0011" | "0100" | "0101" | "0110" | "0111" | "1001" | "1010" | "1011" | "1100" | "1101" | "1110" | "1111";
        if (/^[01]{0,4}$/.test(value)) { // Ensure only binary input
            setSelectionCode(value);

            if (code15digit.length === 15 && value.length === 4) {
                try {
                    const result = generatePackageWithSelectionCode(code15digit, value);
                    setPackageResult(result);
                } catch (error) {
                    setPackageResult("Invalid input or selection code");
                }
            }
        }
    };

    const handleAddConfig = () => {
        const newConfig: Config = {
            package8digit: code15digit.substring(0, 8),
            selection_code: selectionCode,
            data_with_selection_code: [dataWithSelectionCode]
        };

        setEquipmentConfig(prev => {
            const newEquipment = { ...prev };
            // Check if equipment exists
            if (newEquipment.equipment_name) {
                const existingConfig = newEquipment.config.find((config) => config.package8digit === newConfig.package8digit)
                if (existingConfig) {
                    existingConfig.data_with_selection_code.push(dataWithSelectionCode)
                } else {
                    newEquipment.config.push(newConfig)
                }

            }
            return newEquipment
        });
    };

    const handleSave = () => {

        //add equipment_name to equipmentConfig
        setEquipmentConfig(prev => ({
            ...prev,
            equipment_name: equipmentName
        }))
        // onSave(equipmentConfig); // Save the entire equipment configuration
        // handleClose();
    };

    return (
        <Dialog open={open} onClose={handleClose} maxWidth='lg' fullWidth>
            <DialogTitle>Add New Equipment Validate Config</DialogTitle>
            <DialogContent>
                <Box sx={{ bgcolor: 'background.paper', borderRadius: 1, p: 2, m: 2 }}>
                    {/* Level 1: Equipment Name */}
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                label="Equipment Name"
                                value={equipmentName}
                                onChange={(e) => setEquipmentName(e.target.value)}
                                size="small"
                                fullWidth
                            />
                        </Grid>
                    </Grid>
                    <Divider sx={{ pt: 2 }} />

                    {/* Level 2: Package Information */}
                    <Grid container spacing={2} sx={{ pl: 2, pt: 2 }}>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                label="Package Code 15 Digit"
                                value={code15digit}
                                onChange={handleCode15DigitChange}
                                size="small"
                                fullWidth
                                inputProps={{ maxLength: 15 }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                label="First Package Code 8 Digit"
                                value={code15digit.substring(0, 8)}
                                size="small"
                                fullWidth
                                InputProps={{ readOnly: true }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                label="Selection Code (4-digit binary)"
                                value={selectionCode}
                                onChange={handleSelectionCodeChange}
                                size="small"
                                fullWidth
                                inputProps={{ maxLength: 4 }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                label="Package With Selection Code"
                                value={packageResult}
                                size="small"
                                fullWidth
                                InputProps={{ readOnly: true }}
                            />
                        </Grid>
                    </Grid>

                    {/* Level 3: Data with Selection Code */}
                    <Grid container spacing={2} sx={{ pl: 4, pt: 2 }}>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                label="Package With Selection Code"
                                value={dataWithSelectionCode.package_selection_code}
                                onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, package_selection_code: e.target.value })}
                                size="small"
                                fullWidth
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                label="Product Name"
                                value={dataWithSelectionCode.product_name}
                                onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, product_name: e.target.value })}
                                size="small"
                                fullWidth
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                label="Recipe Name"
                                value={dataWithSelectionCode.recipe_name}
                                onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, recipe_name: e.target.value })}
                                size="small"
                                fullWidth
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                select
                                label="Type Validate"
                                defaultValue={'recipe'}
                                value={dataWithSelectionCode.validate_type}
                                onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, validate_type: e.target.value as "recipe" | "toolid" })}
                                size="small"
                                fullWidth
                            >
                                <MenuItem value="recipe">Recipe</MenuItem>
                                <MenuItem value="toolid">Tool Id</MenuItem>
                            </TextField>
                        </Grid>
                        <Grid item xs={12} sm={2}>
                            <TextField
                                label="Operation Code"
                                value={dataWithSelectionCode.operation_code}
                                onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, operation_code: e.target.value })}
                                size="small"
                                fullWidth
                            />
                        </Grid>
                        <Grid item xs={12} sm={2}>
                            <TextField
                                label="On Operation"
                                value={dataWithSelectionCode.on_operation}
                                onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, on_operation: e.target.value })}
                                size="small"
                                fullWidth
                            />
                        </Grid>
                    </Grid>

                    {/* Level 3: Options */}
                    <Box sx={{ pl: 4, display: 'flex', justifyContent: 'space-between', width: "60%" }}>
                        <Grid item xs={12} sm={4}>
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        checked={dataWithSelectionCode.options.use_operation_code}
                                        onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, options: { ...dataWithSelectionCode.options, use_operation_code: e.target.checked } })}
                                        size="small"
                                    />
                                }
                                label={<Typography variant='body2'>Check Operation Code</Typography>}
                            />
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        checked={dataWithSelectionCode.options.use_on_operation}
                                        onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, options: { ...dataWithSelectionCode.options, use_on_operation: e.target.checked } })}
                                        size="small"
                                    />
                                }
                                label={<Typography variant='body2'>Check On Operation</Typography>}
                            />
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        checked={dataWithSelectionCode.options.use_lot_hold}
                                        onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, options: { ...dataWithSelectionCode.options, use_lot_hold: e.target.checked } })}
                                        size="small"
                                    />
                                }
                                label={<Typography variant='body2'>Check Lot Hold</Typography>}
                            />
                        </Grid>
                    </Box>

                    {/* Level 3: Allow Tool IDs */}
                    <Box sx={{ pl: 2 }}>
                        <Typography sx={{ pl: 3 }} variant='body2'> Allow Tool IDs </Typography>
                        <Grid container spacing={2} sx={{ pl: 2, pt: 2 }}>
                            <Grid item xs={12} sm={6}>
                                <TextField size="small" label="Position 1" fullWidth sx={{ mb: 1 }}
                                    value={dataWithSelectionCode.allow_tool_id.position_1.join(',')}
                                    onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, allow_tool_id: { ...dataWithSelectionCode.allow_tool_id, position_1: e.target.value.split(',') } })}
                                />
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <TextField size="small" label="Position 2" fullWidth sx={{ mb: 1 }}
                                    value={dataWithSelectionCode.allow_tool_id.position_2.join(',')}
                                    onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, allow_tool_id: { ...dataWithSelectionCode.allow_tool_id, position_2: e.target.value.split(',') } })}
                                />
                            </Grid>
                        </Grid>
                        <Grid container spacing={2} sx={{ pl: 2, pt: 2 }}>
                            <Grid item xs={12} sm={6}>
                                <TextField size="small" label="Position 3" fullWidth sx={{ mb: 1 }}
                                    value={dataWithSelectionCode.allow_tool_id.position_3.join(',')}
                                    onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, allow_tool_id: { ...dataWithSelectionCode.allow_tool_id, position_3: e.target.value.split(',') } })}
                                />
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <TextField size="small" label="Position 4" fullWidth sx={{ mb: 1 }}
                                    value={dataWithSelectionCode.allow_tool_id.position_4.join(',')}
                                    onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, allow_tool_id: { ...dataWithSelectionCode.allow_tool_id, position_4: e.target.value.split(',') } })}
                                />
                            </Grid>
                        </Grid>
                    </Box>

                    {/* Add Button */}
                    <Divider sx={{ p: 1 }} />
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                        <IconButton color="primary" onClick={handleAddConfig}>
                            <Add />
                        </IconButton>
                    </Box>
                </Box>
                <pre>{JSON.stringify(equipmentConfig, null, 2)}</pre>
            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose}>Cancel</Button>
                <Button onClick={handleSave}>Save</Button>
            </DialogActions>
        </Dialog>
    );
};