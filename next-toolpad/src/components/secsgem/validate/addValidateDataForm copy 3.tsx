'use client';

import {
    Box, Button, Checkbox, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Divider, Grid, TextField, Typography, FormControlLabel,
    IconButton,
    MenuItem
} from '@mui/material';
import React, { useRef, useState } from 'react';
import { EquipmentConfig, Config, DataWithSelectionCode, Options, AllowToolId } from './validatePropsType';
import { Add } from '@mui/icons-material';

export const DialogAddValidateDataForm = (
    { open, onSave, handleClose }:
        {
            open: boolean;
            onSave: (data: EquipmentConfig) => void;
            handleClose: () => void;
        }) => {

    const inputRef = useRef<HTMLInputElement | null>(null);
    const [code15digit, setCode15digit] = useState<string>("");
    const [code8digit, setCode8digit] = useState<string>("");
    const [selectionCode, setSelectionCode] = useState<"1000" | "0000" | "0001" | "0010" | "0011" | "0100" | "0101" | "0110" | "0111" | "1001" | "1010" | "1011" | "1100" | "1101" | "1110" | "1111">("1000");
    const [packageResult, setPackageResult] = useState<string>("");

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

    const handleCode15DigitChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = event.target.value;
        setCode15digit(value);

        // Update dataConfig when code15digit changes
        setDataConfig((prev) => ({ ...prev, package8digit: value.substring(0, 8) })); // <--- Add this line

        if (value.length === 15 && selectionCode.length === 4) {
            try {
                const result = generatePackageWithSelectionCode(value, selectionCode);
                setPackageResult(result);
                // setCode8digit(code15digit.substring(0, 8))
                // setDataConfig({ ...dataConfig, package8digit: code15digit.substring(0, 8) })
            } catch (error) {
                setPackageResult("Invalid input or selection code");
            }
        } else {
            setPackageResult("");
        }
    };

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



    const [equipmentConfig, setEquipmentConfig] = useState<EquipmentConfig>({
        equipment_name: '', config: []
    })

    const [dataConfig, setDataConfig] = useState<Config>({
        package8digit: "",
        selection_code: "1000",
        data_with_selection_code: []
    })

    const [dataWithSelectionCode, setDataWithSelectionCode] = useState<DataWithSelectionCode>({
        package_selection_code: "",
        options: {
            use_operation_code: false,
            use_on_operation: false,
            use_lot_hold: false
        },
        operation_code: "",
        on_operation: "",
        validate_type: "recipe",
        recipe_name: "",
        product_name: "",
        allow_tool_id: {
            position_1: [],
            position_2: [],
            position_3: [],
            position_4: []
        }
    })

    const [optionConfig, setOptionConfig] = useState<Options>({
        use_lot_hold: false,
        use_on_operation: false,
        use_operation_code: false
    })
    const [allowId, setAllowId] = useState<AllowToolId>({
        position_1: [], position_2: [], position_3: [], position_4: []
    })

    const handleSave = () => {
        // console.log(equipmentConfig);
        // console.log(dataConfig);
        // console.log(dataWithSelectionCode);
        // console.log(optionConfig);
        // console.log(allowId);

        setDataConfig((prevConfig) => ({
            ...prevConfig,
            selection_code: selectionCode,
            data_with_selection_code: [...prevConfig.data_with_selection_code, dataWithSelectionCode]
        }))

        setEquipmentConfig((prevConfig) => ({
            ...prevConfig,
            config: [...prevConfig.config, dataConfig]
        }));


        console.log(equipmentConfig);

        // const newConfig: Config = {
        //     package8digit: code15digit.substring(0, 8),
        //     selection_code: selectionCode,
        //     data_with_selection_code: [{
        //         options: {
        //             use_operation_code: false,
        //             use_on_operation: false,
        //             use_lot_hold: false
        //         },
        //         package_selection_code: packageResult,
        //         operation_code: "",
        //         on_operation: "",
        //         validate_type: "recipe",
        //         recipe_name: "",
        //         product_name: "",
        //         allow_tool_id: {
        //             position_1: [],
        //             position_2: [],
        //             position_3: [],
        //             position_4: []
        //         }
        //     }]
        // };

        // const newEquipmentConfig: EquipmentConfig = {
        //     equipment_name: equipmentConfig.equipment_name,
        //     config: [dataConfig]
        // };

        // onSave(newEquipmentConfig);
        // handleClose();


    };

    return (
        <Dialog open={open} onClose={handleClose} maxWidth='lg' fullWidth>
            <DialogTitle>Add New Equipment Validate Config</DialogTitle>
            <DialogContent>
                {/* <DialogContentText>Level 1 Add new equipment config</DialogContentText> */}
                <Box sx={{ bgcolor: 'background.paper', borderRadius: 1, p: 2, m: 2 }}>

                    {/* level 1 */}
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                label="Equipment Name"
                                value={equipmentConfig.equipment_name}
                                onChange={(e) => setEquipmentConfig(prev => ({ ...prev, equipment_name: e.target.value }))}
                                size="small"
                                fullWidth
                            />
                        </Grid>
                    </Grid>
                    <Divider sx={{ pt: 2 }} />

                    {/* level 2 */}
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
                                // onChange={(e) => setDataConfig(prev => ({ ...prev, package8digit: e.target.value }))}
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

                    {/* level 3 */}
                    <Grid container spacing={2} sx={{ pl: 4, pt: 2 }} >
                        <Grid item xs={12} sm={3}>
                            <TextField
                                inputRef={inputRef}
                                label="Package With Selection Code"
                                // value={packageResult}
                                // value={isEditing ? editedData.product_name : dataItem.product_name}
                                // onChange={(e) => setEditedData({ ...editedData, product_name: e.target.value })}
                                onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, package_selection_code: e.target.value })}
                                size="small"
                                fullWidth
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                inputRef={inputRef}
                                label="Product Name"
                                // value={isEditing ? editedData.product_name : dataItem.product_name}
                                // onChange={(e) => setEditedData({ ...editedData, product_name: e.target.value })}
                                onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, product_name: e.target.value })}

                                size="small"
                                fullWidth
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                inputRef={inputRef}
                                label="Recipe Name"
                                // value={isEditing ? editedData.product_name : dataItem.product_name}
                                // onChange={(e) => setEditedData({ ...editedData, product_name: e.target.value })}
                                onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, recipe_name: e.target.value })}
                                size="small"
                                fullWidth
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                // id='validate-type'
                                inputRef={inputRef}
                                // label="Type Validate"
                                select
                                defaultValue={'recipe'}
                                // value={isEditing ? editedData.product_name : dataItem.product_name}
                                // onChange={(e) => setEditedData({ ...editedData, product_name: e.target.value })}
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
                                inputRef={inputRef}
                                label="Operation Code"
                                // value={isEditing ? editedData.product_name : dataItem.product_name}
                                // onChange={(e) => setEditedData({ ...editedData, product_name: e.target.value })}
                                onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, operation_code: e.target.value })}
                                size="small"
                                fullWidth
                            />
                        </Grid>
                        <Grid item xs={12} sm={2}>
                            <TextField
                                inputRef={inputRef}
                                label="On Operation"
                                // value={isEditing ? editedData.product_name : dataItem.product_name}
                                // onChange={(e) => setEditedData({ ...editedData, product_name: e.target.value })}
                                onChange={(e) => setDataWithSelectionCode({ ...dataWithSelectionCode, on_operation: e.target.value })}
                                size="small"
                                fullWidth
                            />
                        </Grid>
                    </Grid>

                    {/* level 3 option */}
                    <Box sx={{ pl: 4, display: 'flex', justifyContent: 'space-between', width: "60%" }}>
                        <Grid item xs={12} sm={4}>
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        // checked={isEditing ? editedData.options.use_operation_code : dataItem.options.use_operation_code}
                                        // onChange={(e) => setEditedData({ ...editedData, options: { ...editedData.options, use_operation_code: e.target.checked } })}
                                        size="small"
                                        onChange={(e) => setOptionConfig({ ...optionConfig, use_operation_code: e.target.checked })}

                                    // disabled={!isEditing}
                                    />
                                }
                                label={<Typography variant='body2'>Check Operation Code</Typography>}
                            />
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        // checked={isEditing ? editedData.options.use_on_operation : dataItem.options.use_on_operation}
                                        // onChange={(e) => setEditedData({ ...editedData, options: { ...editedData.options, use_on_operation: e.target.checked } })}
                                        onChange={(e) => setOptionConfig({ ...optionConfig, use_on_operation: e.target.checked })}

                                        size="small"
                                    // disabled={!isEditing}
                                    />
                                }
                                label={<Typography variant='body2'>Check On Operation</Typography>}
                            />
                        </Grid>
                        <Grid item xs={12} sm={4}>
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        // checked={isEditing ? editedData.options.use_lot_hold : dataItem.options.use_lot_hold}
                                        // onChange={(e) => setEditedData({ ...editedData, options: { ...editedData.options, use_lot_hold: e.target.checked } })}
                                        size="small"
                                        onChange={(e) => setOptionConfig({ ...optionConfig, use_lot_hold: e.target.checked })}

                                    // disabled={!isEditing}
                                    />
                                }
                                label={<Typography variant='body2'>Check Lot Hold</Typography>}
                            />
                        </Grid>
                    </Box>

                    <Box sx={{ pl: 2 }}>
                        <Typography sx={{ pl: 3 }} variant='body2'> Allow Tool IDs </Typography>

                        <Grid container spacing={2} sx={{ pl: 2, pt: 2 }}>
                            <Grid item xs={12} sm={6}>
                                <TextField size="small" label="Position 1" fullWidth sx={{ mb: 1 }}
                                    onChange={(e) => setAllowId({ ...allowId, position_1: e.target.value.split(',') })}
                                />
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <TextField size="small" label="Position 2" fullWidth sx={{ mb: 1 }}
                                    onChange={(e) => setAllowId({ ...allowId, position_2: e.target.value.split(',') })}
                                />
                            </Grid>
                        </Grid>
                        <Grid container spacing={2} sx={{ pl: 2, pt: 2 }}>
                            <Grid item xs={12} sm={6}>
                                <TextField size="small" label="Position 3" fullWidth sx={{ mb: 1 }}
                                    onChange={(e) => setAllowId({ ...allowId, position_3: e.target.value.split(',') })}
                                />

                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <TextField size="small" label="Position 4" fullWidth sx={{ mb: 1 }}
                                    onChange={(e) => setAllowId({ ...allowId, position_4: e.target.value.split(',') })}
                                />
                            </Grid>
                        </Grid>
                    </Box>
                    <Divider sx={{ p: 1 }} />
                    <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
                        <IconButton color="primary"
                        //  onClick={saveEdits}
                        >
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