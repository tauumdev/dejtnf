'use client'
// import { useApiContext } from '@/src/context/apiContext';
import { Add } from '@mui/icons-material';
import { Box, Button, Checkbox, CircularProgress, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Divider, Fade, FormControlLabel, Grid, InputLabel, MenuItem, Select, SelectChangeEvent, TextField, Toolbar, Typography } from '@mui/material';
import React, { useEffect, useRef, useState } from 'react'

import { EquipmentConfig, Config, DataWithSelectionCode, Options, AllowToolId, isBinary4Digit } from './validatePropsType'


export const DialogAddValidateDataForm = (
    { open, onSave, handleClose }:
        {
            open: boolean;
            onSave: () => void;
            handleClose: () => void;
        }) => {

    const inputRef = useRef<HTMLInputElement | null>(null);
    // const [code15digit, setCode15digit] = useState('')

    /**
     * Generates a package name based on a 15-digit input and a 4-digit selection code.
     * @param code15digit - The 15-digit input string.
     * @param selectionCode - The 4-digit binary selection code.
     * @returns The generated package name.
     */
    function generatePackageWithSelectionCode(
        code15digit: string,
        selectionCode: string
    ): string {
        // Validate input lengths
        if (code15digit.length !== 15) {
            throw new Error("The 15-digit code must be exactly 15 characters long.");
        }
        if (selectionCode.length !== 4 || !/^[01]{4}$/.test(selectionCode)) {
            throw new Error("The selection code must be a 4-digit binary string (0 or 1).");
        }

        // Extract parts from the 15-digit code
        const basePackage = code15digit.substring(0, 8); // Positions 1-8
        // const specialMold = code15digit.substring(8, 11); // Positions 9-11
        const specialMold = code15digit[11]; // Position 12
        // const depopulatePin = code15digit[11]; // Position 12
        const depopulatePin = code15digit.substring(12, 14); // Positions 13-14
        const plateType = code15digit[14]; // Positions 13-14
        const additionalInfo = code15digit[14]; // Position 15

        // Parse the selection code
        const [includeBase, includeSpecialMold, includeDepopulatePin, includePlateType] =
            selectionCode.split("").map((digit) => digit === "1");

        // Build the result
        let result = basePackage; // Base package is always included

        if (includeSpecialMold) {
            result += specialMold;
        }
        if (includeDepopulatePin) {
            result += depopulatePin;
        }
        if (includePlateType) {
            result += plateType;
        }

        return result;
    }

    const [code15digit, setCode15digit] = useState<string>("");
    const [selectionCode, setSelectionCode] = useState<string>("1000");
    const [packageResult, setPackageResult] = useState<string>("");

    const [equipmentConfig, setEquipmentConfig] = useState<EquipmentConfig>()
    const [dataWithSelectionCode, setDataWithSelectionCode] = useState<DataWithSelectionCode>()
    const [dataConfig, setDataConfig] = useState<Config>()
    const [optionConfig, setOptionConfig] = useState<Options>()
    const [allowId, setAllowId] = useState<AllowToolId>()

    // Handle changes in the 15-digit input
    const handleCode15DigitChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = event.target.value;
        setCode15digit(value);

        // Automatically generate the package result when the input changes
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

    // Handle changes in the selection code input
    const handleSelectionCodeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const value = event.target.value;
        setSelectionCode(value);

        // Automatically generate the package result when the selection code changes
        if (code15digit.length === 15 && value.length === 4) {
            try {
                const result = generatePackageWithSelectionCode(code15digit, value);
                setPackageResult(result);
            } catch (error) {
                setPackageResult("Invalid input or selection code");
            }
        } else {
            setPackageResult("");
        }
    };

    return (
        <Dialog
            open={open}
            onClose={handleClose}
            aria-labelledby="alert-dialog-title"
            aria-describedby="alert-dialog-description"
            maxWidth='lg'
            fullWidth
        >
            <DialogTitle id="alert-dialog-title">
                {"Add New Equipment Validate Config"}
            </DialogTitle>
            <DialogContent>

                <DialogContentText id="alert-dialog-description">
                    Level 1 Add new equipment config
                </DialogContentText>
                <Box display={'block'} sx={{ bgcolor: 'background.paper', borderRadius: 1, p: 2, m: 2 }}>

                    {/* level 1 */}
                    <Grid container spacing={2} >
                        <Grid item xs={12} sm={3}>
                            <TextField
                                inputRef={inputRef}
                                label="Equipment Name"
                                // value={isEditing ? editedData.product_name : dataItem.product_name}
                                // onChange={(e) => setEditedData({ ...editedData, product_name: e.target.value })}
                                onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                                    setEquipmentConfig(prevState => ({
                                        ...prevState,
                                        equipment_name: event.target.value,
                                        config: prevState?.config || []
                                    }));
                                }}
                                size="small"
                                fullWidth
                            />
                        </Grid>
                    </Grid>
                    <Divider sx={{ pt: 2 }} />
                    {/* level 2 */}
                    <Grid container spacing={2} sx={{ pl: 2, pt: 2 }} >

                        <Grid item xs={12} sm={3}>
                            <TextField
                                label="Package Code 15 Digit"
                                value={code15digit}
                                onChange={handleCode15DigitChange}
                                size="small"
                                fullWidth
                                inputProps={{ maxLength: 15 }} // Limit input to 15 characters

                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                label="First Package Code 8 Digit"
                                value={code15digit ? code15digit.substring(0, 8) : ""}
                                size="small"
                                fullWidth
                                // InputProps={{ readOnly: true }} // Makes it read-only to prevent user edits
                                onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                                    setDataConfig(prevState => ({
                                        ...prevState,
                                        package8digit: event.target.value,
                                        selection_code: prevState?.selection_code || "1000",
                                        data_with_selection_code: prevState?.data_with_selection_code || []
                                    }));
                                }}
                            />
                        </Grid>
                        <Grid item xs={12} sm={3}>
                            <TextField
                                label="Selection Code (4-digit binary)"
                                value={selectionCode}
                                onChange={handleSelectionCodeChange}
                                size="small"
                                fullWidth
                                inputProps={{ maxLength: 4 }} // Limit input to 4 characters
                            />
                        </Grid>

                        <Grid item xs={12} sm={3}>
                            <TextField
                                inputRef={inputRef}
                                label="Package With Selection Code"
                                value={packageResult}
                                // value={isEditing ? editedData.product_name : dataItem.product_name}
                                // onChange={(e) => setEditedData({ ...editedData, product_name: e.target.value })}
                                size="small"
                                fullWidth
                            />
                        </Grid>
                    </Grid>
                    <Divider sx={{ pt: 2 }} />

                    {/* level 3 */}
                    <Grid container spacing={2} sx={{ pl: 4, pt: 2 }} >
                        <Grid item xs={12} sm={3}>
                            <TextField
                                inputRef={inputRef}
                                label="Package With Selection Code"
                                // value={isEditing ? editedData.product_name : dataItem.product_name}
                                // onChange={(e) => setEditedData({ ...editedData, product_name: e.target.value })}
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
                                size="small"
                                fullWidth
                            />
                        </Grid>
                        <Grid item xs={12} sm={2}>
                            <TextField
                                inputRef={inputRef}
                                label="Operation Code"
                                // value={isEditing ? editedData.product_name : dataItem.product_name}
                                // onChange={(e) => setEditedData({ ...editedData, product_name: e.target.value })}
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
                                size="small"
                                fullWidth
                            />
                        </Grid>
                    </Grid>
                    <Box sx={{ pl: 4, display: 'flex', justifyContent: 'space-between', width: "60%" }}>
                        <Grid item xs={12} sm={4}>
                            <FormControlLabel
                                control={
                                    <Checkbox
                                        // checked={isEditing ? editedData.options.use_operation_code : dataItem.options.use_operation_code}
                                        // onChange={(e) => setEditedData({ ...editedData, options: { ...editedData.options, use_operation_code: e.target.checked } })}
                                        size="small"
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
                                    // disabled={!isEditing}
                                    />
                                }
                                label={<Typography variant='body2'>Check Lot Hold</Typography>}
                            />
                        </Grid>
                    </Box>

                    <Box sx={{ pl: 4 }}>
                        <Typography sx={{ p: 1 }} variant='body2'> Allow Tool IDs </Typography>
                        <TextField size="small" label="Position 1" fullWidth sx={{ mb: 1 }} />
                        <TextField size="small" label="Position 2" fullWidth sx={{ mb: 1 }} />
                        <TextField size="small" label="Position 3" fullWidth />
                    </Box>
                    <Divider sx={{ p: 1 }} />
                </Box>

            </DialogContent>
            <DialogActions>
                <Button onClick={handleClose} autoFocus>
                    Cancel
                </Button>
                <Button onClick={onSave} autoFocus>
                    Save
                </Button>
            </DialogActions>
        </Dialog>
    )
}
