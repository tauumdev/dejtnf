'use client';

import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Stepper, Step, StepLabel, Grid, Checkbox, FormControlLabel, IconButton, MenuItem, Select, Tooltip, styled, TooltipProps, tooltipClasses, InputAdornment, FormControl, InputLabel, Popover, Table, TableBody, TableRow, TableCell } from '@mui/material';
import { Add, Delete, HelpOutline } from '@mui/icons-material';
import { EquipmentConfig, Config, DataWithSelectionCode } from '@/src/components/secsgem/validate/validatePropsType';
// import HelpOutlineIcon from "@mui/icons-material/HelpOutline";
import { useApiContext } from '@/src/context/apiContext';

const AddConfigPage = () => {
    const { validate } = useApiContext();
    const [activeStep, setActiveStep] = useState(0);
    const [equipmentName, setEquipmentName] = useState<string>("");

    // Level 2: Package Code และ Selection Code
    const [packages, setPackages] = useState<{ package15digit: string; package8digit: string; selection_code: string; package_selection_code: string }[]>([]);

    // Level 3: Config Data
    const [configData, setConfigData] = useState<DataWithSelectionCode[]>([]);

    const steps = ['Level 1: Equipment Name', 'Level 2: Package Code', 'Level 3: Config Data'];

    const handleNext = () => {
        if (activeStep === 0 && !equipmentName) {
            alert("Please enter Equipment Name");
            return;
        }
        if (activeStep === 1 && packages.length === 0) {
            alert("Please add at least one Package Code");
            return;
        }
        setActiveStep((prevStep) => prevStep + 1);
    };

    const handleBack = () => {
        setActiveStep((prevStep) => prevStep - 1);
    };

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

    const isEquipmentConfigValid = (): boolean => {
        // ตรวจสอบว่า equipment_name ไม่ว่าง
        if (!equipmentName) return false;

        // ตรวจสอบว่า config มีข้อมูล
        if (packages.length === 0) return false;

        // ตรวจสอบว่า data_with_selection_code ในแต่ละ config ไม่ว่าง
        for (const pkg of packages) {
            const configDataForPackage = configData.filter((config) => config.package_selection_code === pkg.package_selection_code);
            if (configDataForPackage.length === 0) return false;
        }

        return true;
    };

    const handleSave = async () => {
        if (!isEquipmentConfigValid()) {
            alert("Please fill in all required fields.");
            return;
        }

        const newConfig: EquipmentConfig = {
            equipment_name: equipmentName,
            config: packages.map((pkg) => ({
                package8digit: pkg.package8digit,
                selection_code: pkg.selection_code,
                data_with_selection_code: configData.filter((config) => config.package_selection_code === pkg.package_selection_code)
            }))
        };
        console.log("New Config:", newConfig);

        // const responseSave = await validate.create(newConfig)
        // console.log(responseSave);
        // if (responseSave.message) {
        //     alert(responseSave.message);
        // } else {
        //     alert("Data saved successfully!");
        // }
        try {
            const responseSave = await validate.create(newConfig)
            if (responseSave.message) {
                alert(responseSave.message);
            } else {
                alert("Data saved successfully!");
            }
        } catch (error) {
            console.log("Error saving data:", responseSave);

            alert(`An error occurred while saving data.${error}`);
        }
    };

    const addPackage = () => {
        const newPackage = { package15digit: "", package8digit: "", selection_code: "1000", package_selection_code: "" };
        setPackages([...packages, newPackage]);
    };

    const removePackage = (index: number) => {
        const newPackages = packages.filter((_, i) => i !== index);
        setPackages(newPackages);
    };

    const handlePackageChange = (index: number, field: string, value: string) => {
        if (field === "selection_code" && !/^[01]{0,4}$/.test(value)) {
            alert("Selection Code must be a 4-digit binary string (0 or 1).");
            return;
        }

        const newPackages = [...packages];

        if (field === "package15digit") {
            // ดึง 8 หลักแรกจาก package15digit
            const package8digit = value.substring(0, 8);

            // ตรวจสอบว่า package8digit ไม่ซ้ำกัน
            const isDuplicate = packages.some((pkg, i) => i !== index && pkg.package8digit === package8digit);
            if (isDuplicate) {
                alert("Package 8 Digit must be unique.");
                return;
            }

            // อัปเดต package8digit และ package15digit
            newPackages[index] = {
                ...newPackages[index],
                package8digit,
                package15digit: value
            };
        } else {
            // อัปเดต field อื่น ๆ
            newPackages[index] = { ...newPackages[index], [field]: value };
        }

        // สร้าง package_selection_code ใหม่
        const package8digit = newPackages[index].package8digit;
        const selectionCode = newPackages[index].selection_code;

        try {
            newPackages[index].package_selection_code = generatePackageWithSelectionCode(
                newPackages[index].package15digit,
                selectionCode
            );
        } catch (error) {
            console.error("Error generating package selection code:", error);
            newPackages[index].package_selection_code = ""; // หรือตั้งค่าเริ่มต้น
        }

        setPackages(newPackages);
    };

    const addConfigData = () => {

        setConfigData([
            ...configData,
            {
                options: {
                    use_operation_code: false,
                    use_on_operation: false,
                    use_lot_hold: false
                },
                package_selection_code: "",
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
            }
        ]);
    };

    const removeConfigData = (index: number) => {
        const newConfigData = configData.filter((_, i) => i !== index);
        setConfigData(newConfigData);
    };

    const handleConfigDataChange = (index: number, field: string, value: any) => {
        const newConfigData = [...configData];
        newConfigData[index] = { ...newConfigData[index], [field]: value };
        setConfigData(newConfigData);
    };

    const CustomWidthTooltip = styled(({ className, ...props }: TooltipProps) => (
        <Tooltip {...props} classes={{ popper: className }} />
    ))({
        [`& .${tooltipClasses.tooltip}`]: {
            maxWidth: 500,
        },
    });

    // คำอธิบายสำหรับแต่ละ digit ใน selection_code
    const selectionCodeTooltip = (
        <Box display={'block'} sx={{ p: 2 }}>
            <Typography variant='body2'><strong>Digit 1:</strong> Use Base Package (Positions 1-8 in 15-digit code)</Typography>
            <Typography variant='body2'><strong>Digit 2:</strong> Use Special Mold (Positions 12 in 15-digit code)</Typography>
            <Typography variant='body2'><strong>Digit 3:</strong> Use Depopulate Pin (Positions 13-14 in 15-digit code)</Typography>
            <Typography variant='body2'><strong>Digit 4:</strong> Use Plate Type (Position 15 in 15-digit code)</Typography>
        </Box>
    );

    const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
    const open = Boolean(anchorEl);
    return (
        <Box sx={{ width: '100%', p: 4 }}>
            <Stepper activeStep={activeStep} alternativeLabel>
                {steps.map((label) => (
                    <Step key={label}>
                        <StepLabel>{label}</StepLabel>
                    </Step>
                ))}
            </Stepper>

            {activeStep === 0 && (
                <Box sx={{ mt: 4 }}>
                    <Typography variant="h6">Level 1: Equipment Name</Typography>
                    <TextField
                        autoComplete='off'
                        size='small'
                        label="Equipment Name"
                        value={equipmentName}
                        onChange={(e) => setEquipmentName(e.target.value)}
                        fullWidth
                        sx={{ mt: 2 }}
                    />
                </Box>
            )}

            {activeStep === 1 && (
                <Box sx={{ mt: 4 }}>
                    <Typography variant="h6">Level 2: Package Code</Typography>
                    {packages.map((pkg, index) => (
                        <Grid container spacing={2} key={index} sx={{ mt: 2 }}>
                            <Grid item xs={3}>
                                <TextField
                                    autoComplete='off'
                                    size='small'
                                    label="Package Code 15 Digit"
                                    value={pkg.package15digit}
                                    onChange={(e) => handlePackageChange(index, "package15digit", e.target.value)}
                                    fullWidth
                                    inputProps={{ maxLength: 15 }}
                                    error={pkg.package15digit.length !== 15}
                                />
                            </Grid>
                            <Grid item xs={2}>
                                <TextField
                                    autoComplete='off'
                                    size='small'
                                    label="First 8 Digit"
                                    value={pkg.package8digit}
                                    fullWidth
                                    InputProps={{ readOnly: true }} // ไม่ให้แก้ไขโดยตรง
                                />
                            </Grid>

                            {/* <Grid item xs={2}>
                                <TextField
                                    autoComplete='off'
                                    size='small'
                                    label="Selection Code (4-digit binary)"
                                    value={pkg.selection_code}
                                    onChange={(e) => handlePackageChange(index, "selection_code", e.target.value)}
                                    fullWidth
                                    inputProps={{
                                        maxLength: 4, // จำกัดความยาว 4 หลัก
                                        pattern: "[01]*", // รับเฉพาะ 0 และ 1
                                        inputMode: "numeric" // แสดงแป้นตัวเลขบนมือถือ
                                    }}
                                    color={pkg.selection_code.length !== 4 ? "error" : "info"}
                                />
                            </Grid> */}

                            <Grid item xs={3}>
                                <TextField
                                    autoComplete='off'
                                    size='small'
                                    label="Selection Code (4-digit binary)"
                                    value={pkg.selection_code}
                                    onChange={(e) => handlePackageChange(index, "selection_code", e.target.value)}
                                    fullWidth
                                    inputProps={{
                                        maxLength: 4, // จำกัดความยาว 4 หลัก
                                        pattern: "[01]*", // รับเฉพาะ 0 และ 1
                                        inputMode: "numeric" // แสดงแป้นตัวเลขบนมือถือ
                                    }}
                                    error={pkg.selection_code.length !== 4}
                                    InputProps={{
                                        endAdornment: (
                                            <InputAdornment position="end">
                                                <IconButton
                                                    onClick={(e) => setAnchorEl(e.currentTarget)}
                                                    edge="end"
                                                >
                                                    <HelpOutline fontSize="small" />
                                                </IconButton>
                                            </InputAdornment>
                                        ),
                                    }}
                                />
                                <Popover
                                    id="selection-code-popover"
                                    open={open}
                                    anchorEl={anchorEl}
                                    onClose={() => setAnchorEl(null)}
                                // anchorOrigin={{
                                //     // vertical: 'bottom',
                                //     // horizontal: 'left',
                                // }}
                                >
                                    <Box sx={{ p: 1 }}>
                                        <Table size="small">
                                            <TableBody>
                                                <TableRow>
                                                    <TableCell>
                                                        <Typography variant="body2"><strong>Digit 1:</strong></Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2">Use Base Package (Positions 1-8 in 15-digit code)</Typography>
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>
                                                        <Typography variant="body2"><strong>Digit 2:</strong></Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2">Use Special Mold (Position 12 in 15-digit code)</Typography>
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>
                                                        <Typography variant="body2"><strong>Digit 3:</strong></Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2">Use Depopulate Pin (Positions 13-14 in 15-digit code)</Typography>
                                                    </TableCell>
                                                </TableRow>
                                                <TableRow>
                                                    <TableCell>
                                                        <Typography variant="body2"><strong>Digit 4:</strong></Typography>
                                                    </TableCell>
                                                    <TableCell>
                                                        <Typography variant="body2">Use Plate Type (Position 15 in 15-digit code)</Typography>
                                                    </TableCell>
                                                </TableRow>
                                            </TableBody>
                                        </Table>
                                    </Box>
                                </Popover>
                            </Grid>

                            <Grid item xs={3}>
                                <TextField
                                    autoComplete='off'
                                    size='small'
                                    label="Package With Selection Code"
                                    value={pkg.package_selection_code}
                                    fullWidth
                                    InputProps={{ readOnly: true }}
                                />
                            </Grid>
                            <Grid item xs={1}>
                                <IconButton onClick={() => removePackage(index)}>
                                    <Delete />
                                </IconButton>
                            </Grid>
                        </Grid>
                    ))}
                    <Button variant="outlined" startIcon={<Add />} onClick={addPackage} sx={{ mt: 2 }}>
                        Add Package
                    </Button>
                </Box>
            )}

            {activeStep === 2 && (
                <Box sx={{ mt: 4 }}>
                    <Typography variant="h6">Level 3: Config Data</Typography>
                    {configData.map((config, index) => (
                        <Box key={index} sx={{ mt: 2, p: 2, border: '1px solid #ccc', borderRadius: 1 }}>
                            <Grid container spacing={2}>
                                <Grid item xs={12}>
                                    <Select
                                        autoComplete='off'
                                        size='small'
                                        value={config.package_selection_code}
                                        onChange={(e) => handleConfigDataChange(index, "package_selection_code", e.target.value)}
                                        fullWidth
                                        displayEmpty
                                    >
                                        <MenuItem value="" disabled>
                                            Select Package Selection Code
                                        </MenuItem>
                                        {packages.map((pkg, i) => (
                                            <MenuItem key={i} value={pkg.package_selection_code}>
                                                {pkg.package_selection_code}
                                            </MenuItem>
                                        ))}
                                    </Select>
                                </Grid>

                                <Grid item xs={12} sm={3}>
                                    <TextField
                                        autoComplete='off'
                                        size='small'
                                        label="Product Name"
                                        value={config.product_name}
                                        onChange={(e) => handleConfigDataChange(index, "product_name", e.target.value)}
                                        fullWidth
                                    />
                                </Grid>
                                <Grid item xs={12} sm={3}>
                                    <TextField
                                        autoComplete='off'
                                        size='small'
                                        label="Recipe Name"
                                        value={config.recipe_name}
                                        onChange={(e) => handleConfigDataChange(index, "recipe_name", e.target.value)}
                                        fullWidth
                                    />
                                </Grid>
                                <Grid item xs={12} sm={2}>
                                    {/* <Select
                                        autoComplete='off'
                                        size='small'
                                        value={config.validate_type}
                                        defaultValue='recipe'
                                        onChange={(e) => handleConfigDataChange(index, "validate_type", e.target.value)}
                                        fullWidth
                                        displayEmpty
                                    >
                                        <MenuItem value="" disabled>
                                            Validate Type
                                        </MenuItem>
                                        <MenuItem value="recipe" > Recipe </MenuItem>
                                        <MenuItem value="tool_id" > Tool Id </MenuItem>

                                    </Select> */}
                                    <TextField
                                        size='small'
                                        select
                                        label="Validate Type"
                                        defaultValue="recipe"
                                        fullWidth
                                        onChange={(e) => handleConfigDataChange(index, "validate_type", e.target.value)}
                                    >
                                        <MenuItem value="" disabled>
                                            Validate Type
                                        </MenuItem>
                                        <MenuItem value="recipe" > Recipe </MenuItem>
                                        <MenuItem value="tool_id" > Tool Id </MenuItem>

                                    </TextField>
                                </Grid>
                                <Grid item xs={12} sm={2}>
                                    <TextField
                                        autoComplete='off'
                                        size='small'
                                        label="Operation Code"
                                        value={config.operation_code}
                                        onChange={(e) => handleConfigDataChange(index, "operation_code", e.target.value)}
                                        fullWidth
                                    />
                                </Grid>
                                <Grid item xs={12} sm={2}>
                                    <TextField
                                        autoComplete='off'
                                        size='small'
                                        label="On Operation"
                                        value={config.on_operation}
                                        onChange={(e) => handleConfigDataChange(index, "on_operation", e.target.value)}
                                        fullWidth
                                    />
                                </Grid>

                                {/* options */}
                                <Grid item xs={12} sm={4}>
                                    <FormControlLabel
                                        control={
                                            <Checkbox
                                                checked={config.options.use_on_operation}
                                                onChange={(e) => handleConfigDataChange(index, "options", {
                                                    ...config.options,
                                                    use_on_operation: e.target.checked
                                                })}
                                            />
                                        }
                                        // label="Check On Operation"
                                        label={
                                            <Typography variant="body2">Check On Operation</Typography> // ทำให้ตัวหนังสือเล็กลง
                                        }
                                    />
                                </Grid>

                                <Grid item xs={12} sm={4}>
                                    <FormControlLabel
                                        control={
                                            <Checkbox
                                                checked={config.options.use_operation_code}
                                                onChange={(e) => handleConfigDataChange(index, "options", {
                                                    ...config.options,
                                                    use_operation_code: e.target.checked
                                                })}
                                            />
                                        }
                                        // label="Check Operation Code"
                                        label={
                                            <Typography variant="body2">Check Operation Code</Typography> // ทำให้ตัวหนังสือเล็กลง
                                        }
                                    />
                                </Grid>
                                <Grid item xs={12} sm={4}>
                                    <FormControlLabel
                                        control={
                                            <Checkbox
                                                checked={config.options.use_lot_hold}
                                                onChange={(e) => handleConfigDataChange(index, "options", {
                                                    ...config.options,
                                                    use_lot_hold: e.target.checked
                                                })}
                                            />
                                        }
                                        // label="Check Lot Hold"
                                        label={
                                            <Typography variant="body2">Check Lot Hold</Typography> // ทำให้ตัวหนังสือเล็กลง
                                        }
                                    />
                                </Grid>
                                {/* allow tool ids */}
                                <Grid item xs={12} sm={12}>
                                    <Typography>Allow Tool Ids</Typography>
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                    <TextField
                                        autoComplete='off'
                                        size='small'
                                        label="Position 1"
                                        // value={config.recipe_name}
                                        onChange={(e) => handleConfigDataChange(index, "allow_tool_id", {
                                            ...config.allow_tool_id, position_1: e.target.value.split(',')
                                        })}
                                        fullWidth
                                    />
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                    <TextField
                                        autoComplete='off'
                                        size='small'
                                        label="Position 2"
                                        // value={config.recipe_name}
                                        onChange={(e) => handleConfigDataChange(index, "allow_tool_id", {
                                            ...config.allow_tool_id, position_2: e.target.value.split(',')
                                        })}
                                        fullWidth
                                    />
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                    <TextField
                                        autoComplete='off'
                                        size='small'
                                        label="Position 3"
                                        // value={config.recipe_name}
                                        onChange={(e) => handleConfigDataChange(index, "allow_tool_id", {
                                            ...config.allow_tool_id, position_3: e.target.value.split(',')
                                        })}
                                        fullWidth
                                    />
                                </Grid>
                                <Grid item xs={12} sm={6}>
                                    <TextField
                                        autoComplete='off'
                                        size='small'
                                        label="Position 4"
                                        // value={config.recipe_name}
                                        onChange={(e) => handleConfigDataChange(index, "allow_tool_id", {
                                            ...config.allow_tool_id, position_4: e.target.value.split(',')
                                        })}
                                        fullWidth
                                    />
                                </Grid>

                                <Grid item xs={12}>
                                    <IconButton onClick={() => removeConfigData(index)}>
                                        <Delete />
                                    </IconButton>
                                </Grid>
                            </Grid>
                        </Box>
                    ))}
                    <Button variant="outlined" startIcon={<Add />} onClick={addConfigData} sx={{ mt: 2 }}>
                        Add Config Data
                    </Button>
                </Box>
            )}

            <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 4 }}>
                {activeStep !== 0 && (
                    <Button onClick={handleBack} sx={{ mr: 2 }}>
                        Back
                    </Button>
                )}
                {activeStep === steps.length - 1 ? (
                    <Button
                        variant="contained"
                        onClick={handleSave}
                        disabled={!isEquipmentConfigValid()} // ปิดการใช้งานหากข้อมูลไม่ครบถ้วน
                    >
                        Save
                    </Button>
                ) : (
                    <Button variant="contained" onClick={handleNext}>
                        Next
                    </Button>
                )}
            </Box>
        </Box>
    );
};

export default AddConfigPage;