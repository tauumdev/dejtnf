'use client';

import React, { useState } from 'react';
import {
    Card,
    CardContent,
    Typography,
    Button,
    TextField,
    Accordion,
    AccordionSummary,
    AccordionDetails,
    Checkbox,
    FormControlLabel,
    IconButton,
    Grid
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import DeleteIcon from '@mui/icons-material/Delete';

export default function DynamicEquipmentForm() {
    const [equipments, setEquipments] = useState([]);

    const handleAddEquipment = () => {
        setEquipments((prev) => [
            ...prev,
            {
                equipment_name: '',
                config: []
            }
        ]);
    };

    const handleRemoveEquipment = (index) => {
        setEquipments((prev) => prev.filter((_, i) => i !== index));
    };

    const handleEquipmentChange = (index, field, value) => {
        setEquipments((prev) =>
            prev.map((eq, i) => (i === index ? { ...eq, [field]: value } : eq))
        );
    };

    const handleAddPackage = (equipmentIndex) => {
        setEquipments((prev) =>
            prev.map((eq, i) =>
                i === equipmentIndex
                    ? {
                        ...eq,
                        config: [
                            ...eq.config,
                            {
                                package8digit: '',
                                selection_code: '',
                                data_with_selection_code: []
                            }
                        ]
                    }
                    : eq
            )
        );
    };

    const handleRemovePackage = (equipmentIndex, packageIndex) => {
        setEquipments((prev) =>
            prev.map((eq, i) =>
                i === equipmentIndex
                    ? {
                        ...eq,
                        config: eq.config.filter((_, j) => j !== packageIndex)
                    }
                    : eq
            )
        );
    };

    const handlePackageChange = (equipmentIndex, packageIndex, field, value) => {
        setEquipments((prev) =>
            prev.map((eq, i) =>
                i === equipmentIndex
                    ? {
                        ...eq,
                        config: eq.config.map((pkg, j) =>
                            j === packageIndex ? { ...pkg, [field]: value } : pkg
                        )
                    }
                    : eq
            )
        );
    };

    const handleAddDataSelection = (equipmentIndex, packageIndex) => {
        setEquipments((prev) =>
            prev.map((eq, i) =>
                i === equipmentIndex
                    ? {
                        ...eq,
                        config: eq.config.map((pkg, j) =>
                            j === packageIndex
                                ? {
                                    ...pkg,
                                    data_with_selection_code: [
                                        ...pkg.data_with_selection_code,
                                        {
                                            package_selection_code: '',
                                            operation_code: '',
                                            on_operation: '',
                                            validate_type: '',
                                            recipe_name: '',
                                            product_name: '',
                                            options: {
                                                use_operation_code: false,
                                                use_on_operation: false,
                                                use_lot_hold: false
                                            },
                                            tool_id: {
                                                tool_1: [],
                                                tool_2: [],
                                                tool_3: [],
                                                tool_4: []
                                            }
                                        }
                                    ]
                                }
                                : pkg
                        )
                    }
                    : eq
            )
        );
    };

    const handleDataSelectionChange = (equipmentIndex, packageIndex, dataIndex, field, value) => {
        setEquipments((prev) =>
            prev.map((eq, i) =>
                i === equipmentIndex
                    ? {
                        ...eq,
                        config: eq.config.map((pkg, j) =>
                            j === packageIndex
                                ? {
                                    ...pkg,
                                    data_with_selection_code: pkg.data_with_selection_code.map((data, k) =>
                                        k === dataIndex ? { ...data, [field]: value } : data
                                    )
                                }
                                : pkg
                        )
                    }
                    : eq
            )
        );
    };

    const handleOptionChange = (equipmentIndex, packageIndex, dataIndex, optionField, checked) => {
        setEquipments((prev) =>
            prev.map((eq, i) =>
                i === equipmentIndex
                    ? {
                        ...eq,
                        config: eq.config.map((pkg, j) =>
                            j === packageIndex
                                ? {
                                    ...pkg,
                                    data_with_selection_code: pkg.data_with_selection_code.map((data, k) =>
                                        k === dataIndex
                                            ? {
                                                ...data,
                                                options: {
                                                    ...data.options,
                                                    [optionField]: checked
                                                }
                                            }
                                            : data
                                    )
                                }
                                : pkg
                        )
                    }
                    : eq
            )
        );
    };

    return (
        <Card>
            <CardContent>
                <Typography variant="h5">Dynamic Equipment Config</Typography>
                <Button variant="contained" color="primary" onClick={handleAddEquipment} sx={{ my: 2 }}>
                    Add Equipment
                </Button>
                {equipments.map((equipment, eqIndex) => (
                    <Accordion key={eqIndex}>
                        <AccordionSummary expandIcon={<ExpandMoreIcon />}
                            sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography>{equipment.equipment_name || `Equipment ${eqIndex + 1}`}</Typography>
                            {/* <IconButton onClick={() => handleRemoveEquipment(eqIndex)}><DeleteIcon /></IconButton> */}
                        </AccordionSummary>
                        <AccordionDetails>
                            <TextField
                                label="Equipment Name"
                                value={equipment.equipment_name}
                                onChange={(e) => handleEquipmentChange(eqIndex, 'equipment_name', e.target.value)}
                                fullWidth
                                sx={{ my: 1 }}
                            />
                            <Button variant="outlined" onClick={() => handleAddPackage(eqIndex)}>
                                Add Package
                            </Button>
                            {equipment.config.map((pkg, pkgIndex) => (
                                <Accordion key={pkgIndex} sx={{ mt: 2 }}>
                                    <AccordionSummary expandIcon={<ExpandMoreIcon />}
                                        sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <Typography>{pkg.package8digit || `Package ${pkgIndex + 1}`}</Typography>
                                        {/* <IconButton onClick={() => handleRemovePackage(eqIndex, pkgIndex)}><DeleteIcon /></IconButton> */}
                                    </AccordionSummary>
                                    <AccordionDetails>
                                        <TextField
                                            label="Package 8 Digit"
                                            value={pkg.package8digit}
                                            onChange={(e) => handlePackageChange(eqIndex, pkgIndex, 'package8digit', e.target.value)}
                                            fullWidth
                                            sx={{ my: 1 }}
                                        />
                                        <TextField
                                            label="Selection Code"
                                            value={pkg.selection_code}
                                            onChange={(e) => handlePackageChange(eqIndex, pkgIndex, 'selection_code', e.target.value)}
                                            fullWidth
                                            sx={{ my: 1 }}
                                        />
                                        <Button variant="outlined" onClick={() => handleAddDataSelection(eqIndex, pkgIndex)}>
                                            Add Data with Selection Code
                                        </Button>
                                        {pkg.data_with_selection_code.map((data, dataIndex) => (
                                            <Grid container spacing={2} key={dataIndex} sx={{ mt: 2 }}>
                                                <Grid item xs={12} sm={6}>
                                                    <TextField
                                                        label="Package Selection Code"
                                                        value={data.package_selection_code}
                                                        onChange={(e) => handleDataSelectionChange(eqIndex, pkgIndex, dataIndex, 'package_selection_code', e.target.value)}
                                                        fullWidth
                                                    />
                                                </Grid>
                                                <Grid item xs={12} sm={6}>
                                                    <TextField
                                                        label="Operation Code"
                                                        value={data.operation_code}
                                                        onChange={(e) => handleDataSelectionChange(eqIndex, pkgIndex, dataIndex, 'operation_code', e.target.value)}
                                                        fullWidth
                                                    />
                                                </Grid>
                                                <Grid item xs={12}>
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={data.options.use_operation_code}
                                                                onChange={(e) => handleOptionChange(eqIndex, pkgIndex, dataIndex, 'use_operation_code', e.target.checked)}
                                                            />
                                                        }
                                                        label="Use Operation Code"
                                                    />
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={data.options.use_on_operation}
                                                                onChange={(e) => handleOptionChange(eqIndex, pkgIndex, dataIndex, 'use_on_operation', e.target.checked)}
                                                            />
                                                        }
                                                        label="Use On Operation"
                                                    />
                                                    <FormControlLabel
                                                        control={
                                                            <Checkbox
                                                                checked={data.options.use_lot_hold}
                                                                onChange={(e) => handleOptionChange(eqIndex, pkgIndex, dataIndex, 'use_lot_hold', e.target.checked)}
                                                            />
                                                        }
                                                        label="Use Lot Hold"
                                                    />
                                                </Grid>
                                            </Grid>
                                        ))}
                                    </AccordionDetails>
                                </Accordion>
                            ))}
                        </AccordionDetails>
                    </Accordion>
                ))}
            </CardContent>
        </Card>
    );
}
