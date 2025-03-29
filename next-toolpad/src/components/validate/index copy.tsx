'use client'
import { Autocomplete, Button, Grid2, MenuItem, TextField } from '@mui/material';
import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { useApiContext } from '@/src/context/apiContext';
import type { ValidateConfig, ConfigItem, DataWithSelectionCode } from './validatePropsType';
import { v4 as uuidv4 } from 'uuid';
import MemoizedAccordionItem from './memoizedAccordionItem';
import { SnackbarNotify } from '../snackbar';
import { DialogConfirm } from '../dialogConfirm';

interface User {
    name: string;
    email: string;
    role: string;
}

interface ValidateConfigProps {
    user: User;
}

// Handle errors from API requests
const handleError = (error: any, defaultMessage: string): string => {
    // console.log(error); // Log the error for debugging

    // Handle array of errors (e.g., validation errors)
    if (Array.isArray(error)) {
        return error
            .map((err: any) => {
                const fieldName = err.param || 'field';
                const errorMsg = err.msg || 'Invalid value';
                return `${fieldName}: ${errorMsg}`;
            })
            .join(', ');
    }

    // Handle error objects (e.g., Axios error responses)
    if (typeof error === 'object' && error !== null) {
        // Check for server validation errors
        if (error.response?.data?.errors) {
            return error.response.data.errors.msg || defaultMessage;
        }
        // Check for generic error messages
        if (error.message) {
            return error.message;
        }
        // Fallback to string representation
        return error.toString();
    }

    // Handle string errors
    if (typeof error === 'string') {
        return error;
    }

    // Return the default message if the error type is unknown
    return defaultMessage;
};

export default function ValidateConfigComponent(props: ValidateConfigProps): JSX.Element {
    const { user } = props;
    const { validate } = useApiContext();
    const [equipmentList, setEquipmentList] = useState<ValidateConfig[]>([]);
    const [selectedEquipmentName, setSelectedEquipmentName] = useState('');
    const [selectedPackage8Digit, setSelectedPackage8Digit] = useState('');
    const [selectedSelectCode, setSelectedSelectCode] = useState<"1000" | "1001" | "1010" | "1011" | "1100" | "1101" | "1110" | "1111">('1000');
    const [displayData, setDisplayData] = useState<DataWithSelectionCode[]>([]);
    const [editKey, setEditKey] = useState<string[]>([]);
    const [expandedAccordions, setExpandedAccordions] = useState<string[]>([]);

    // State variables for Snackbar
    const [openSnackbar, setOpenSnackbar] = useState(false);
    const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error' | 'info' | 'warning'>('success');
    const [snackbarMessage, setSnackbarMessage] = useState('');

    const [openDialog, setOpenDialog] = useState(false)
    const [dialogTitle, setDialogTitle] = useState('')
    const [dialogMessage, setDialogMessage] = useState('')
    const [actionBtnText, setActionBtnText] = useState<"CREATE" | "DELETE" | "UPDATE">('CREATE');
    const [actionBtnColor, setActionBtnColor] = useState<'success' | 'error' | 'info' | 'warning'>('success');

    // Function to refresh data
    const refreshData = useCallback(async () => {
        const res = await validate.gets(undefined, undefined, 1, 100, 'equipment_name', 1);
        setEquipmentList(res.docs || []);
    }, [validate]);

    // Fetch equipment list
    useEffect(() => {
        refreshData();
    }, []);

    const equipmentExist = useCallback(() => {
        return equipmentList.find((item) => item.equipment_name === selectedEquipmentName);
    }, [selectedEquipmentName, equipmentList]);

    const equipment8DigitExist = useCallback(() => {
        return equipmentList
            .find(item => item.equipment_name === selectedEquipmentName)?.config
            .find(item => item.package8digit === selectedPackage8Digit);
    }, [selectedPackage8Digit, selectedEquipmentName, equipmentList]);

    useEffect(() => {
        if (selectedPackage8Digit && selectedPackage8Digit.length == 8) {
            const foundPackage = equipment8DigitExist();
            if (foundPackage) {
                // setIsNew8Digit(false);
                setSelectedSelectCode(foundPackage.selection_code);
                setDisplayData(foundPackage.data_with_selection_code);
            } else {
                // setIsNew8Digit(true);
                setDisplayData([]);
            }
        } else {
            if (selectedEquipmentName) {
                const foundEquipment = equipmentExist();
                if (foundEquipment) {
                    // setIsNewEquipment(false);
                    setDisplayData(foundEquipment.config.flatMap(config => config.data_with_selection_code) || []);
                } else {
                    // setIsNewEquipment(true);
                    setDisplayData([]);
                }
            } else {
                // setIsNewEquipment(true);
                setDisplayData([]);
            }
        }
    }, [selectedPackage8Digit, equipment8DigitExist, equipmentExist, selectedEquipmentName]);

    const canAdd = useCallback(() => {
        return selectedEquipmentName && selectedPackage8Digit && selectedSelectCode &&
            !(selectedSelectCode === '1000' && displayData.length >= 1);
    }, [selectedEquipmentName, selectedPackage8Digit, selectedSelectCode, displayData.length]);

    const handleAdd = useCallback(() => {
        const newId = `NewSelectionCode,${uuidv4()}`;
        const newPackage: DataWithSelectionCode = {
            package_selection_code: newId,
            product_name: 'New Package',
            validate_type: 'recipe',
            recipe_name: '',
            operation_code: '',
            on_operation: '',
            options: {
                use_operation_code: false,
                use_on_operation: false,
                use_lot_hold: false
            },
            allow_tool_id: {
                position_1: [],
                position_2: [],
                position_3: [],
                position_4: [],
            }
        };
        // setIsNew8Digit(true)
        setDisplayData(prevData => [newPackage, ...prevData]);
        setExpandedAccordions(prev => [...prev, newId]);
        setEditKey(prev => [...prev, newId]);
    }, []);

    const handleItemToggle = useCallback((id: string) => {
        setExpandedAccordions(prev =>
            prev.includes(id)
                ? prev.filter(item => item !== id)
                : [...prev, id]
        );
    }, []);

    const handleItemEdit = useCallback((id: string) => {
        setEditKey(prev => [...prev, id]);
    }, []);

    const isNewEquipment = useMemo(() => {
        return !equipmentList.some((item) => item.equipment_name === selectedEquipmentName);
    }, [selectedEquipmentName, equipmentList]);

    const isNew8Digit = useMemo(() => {
        return !equipmentList
            .find(item => item.equipment_name === selectedEquipmentName)
            ?.config.some(item => item.package8digit === selectedPackage8Digit);
    }, [selectedPackage8Digit, selectedEquipmentName, equipmentList]);

    const handleItemCancel = useCallback((id: string) => {
        setEditKey(prev => prev.filter(k => k !== id));
    }, []);

    // Function to handle API requests with success and error handling
    const handleApiRequest = async (requestFn: () => Promise<any>, successMessage: string, errorMessage: string) => {
        try {
            const response = await requestFn();
            setSnackbarSeverity('success');
            setSnackbarMessage(successMessage);
            setOpenSnackbar(true);
            refreshData();
            return response;
        } catch (error) {
            const messages = handleError(error, errorMessage);
            setSnackbarSeverity('error');
            setSnackbarMessage(messages);
            setOpenSnackbar(true);
            throw error;
        }
    };


    const [createValidateConfig, setCreateValidateConfig] = useState<ValidateConfig>()
    const handleCreate = async () => {
        await handleApiRequest(
            () => validate.create(createValidateConfig!),
            `Create successfully`,
            'An error occurred while create data')
    }

    const [updateValidateConfig, setUpdateValidateConfig] = useState<ValidateConfig>()
    const handleUpdate = async () => {
        await handleApiRequest(
            () => validate.update(updateValidateConfig!._id!, updateValidateConfig!),
            `Update successfully`,
            'An error occurred while update data')
    }

    const [deleteId, setDeleteId] = useState<string | null>(null);
    const handleDelete = async () => {
        await handleApiRequest(
            () => validate.delete(deleteId!),
            `Delete successfully`,
            'An error occurred while delete data')
    }

    const onConfirm = () => {
        if (actionBtnText === 'CREATE') {
            handleCreate();
        } else if (actionBtnText === 'UPDATE') {
            handleUpdate();
        } else if (actionBtnText === 'DELETE') {
            handleDelete();
        }
        setOpenDialog(false);
    }
    const handleItemSave = useCallback(async (id: string, newData: DataWithSelectionCode) => {
        // 1. Validation
        const isDuplicate = displayData.some(
            item => item.package_selection_code === newData.package_selection_code &&
                item.package_selection_code !== id
        );
        if (isDuplicate) {
            alert('Package Selection Code must be unique!');
            return;
        }

        // 2. Prepare data
        let equipmentToSave: ValidateConfig;
        const isNew = isNewEquipment;

        if (isNew) {
            equipmentToSave = {
                equipment_name: selectedEquipmentName,
                config: [{
                    package8digit: selectedPackage8Digit,
                    selection_code: selectedSelectCode,
                    data_with_selection_code: displayData.map(item =>
                        item.package_selection_code === id ? newData : item
                    )
                }]
            };
        } else {

            const existingEquipment = equipmentExist()
            if (!existingEquipment) throw new Error('Equipment not found');

            equipmentToSave = {
                ...existingEquipment,
                config: isNew8Digit
                    ? [...existingEquipment.config, {
                        package8digit: selectedPackage8Digit,
                        selection_code: selectedSelectCode,
                        data_with_selection_code: displayData.map(item =>
                            item.package_selection_code === id ? newData : item
                        )
                    }]
                    : existingEquipment.config.map(config =>
                        config.package8digit === selectedPackage8Digit
                            ? {
                                ...config,
                                selection_code: selectedSelectCode,// as "1000" | "1001" | "1010" | "1011" | "1100" | "1101" | "1110" | "1111",
                                data_with_selection_code: displayData.map(item =>
                                    item.package_selection_code === id ? newData : item
                                )
                            }
                            : config
                    )
            };
        }

        // 3. Optimistic UI update
        const prevData = [...displayData];
        setDisplayData(prev => prev.map(item =>
            item.package_selection_code === id ? newData : item
        ));

        try {
            // 4. Save to API
            // const response = isNew
            //     ? await validate.create(equipmentToSave)
            //     : await validate.update(equipmentToSave._id!, equipmentToSave);

            if (isNew) {
                setCreateValidateConfig(equipmentToSave);
                setDialogTitle(`Confirm create validate config: ${selectedEquipmentName}`);
                setDialogMessage(`Are you sure you want to create?: ${newData.product_name}`);
                setActionBtnText('CREATE');
                setActionBtnColor('success');
                setOpenDialog(true);
            } else {
                setUpdateValidateConfig(equipmentToSave);
                setDialogTitle(`Confirm update validate config: ${selectedEquipmentName}`);
                setDialogMessage(`Are you sure you want to update?: ${newData.product_name}`);
                setActionBtnText('UPDATE');
                setActionBtnColor('success');
                setOpenDialog(true);
            }

            // 5. Refresh data
            refreshData();

            // 6. Update UI states
            setEditKey(prev => prev.filter(k => k !== id));
            if (id !== newData.package_selection_code) {
                setExpandedAccordions(prev =>
                    prev.includes(id)
                        ? [...prev.filter(item => item !== id), newData.package_selection_code]
                        : prev
                );
            }

        } catch (error) {
            // Rollback on error
            setDisplayData(prevData);
            setSnackbarSeverity('error');
            setSnackbarMessage(error);
            setOpenSnackbar(true);
        }

    }, [displayData, isNew8Digit, isNewEquipment, selectedEquipmentName, selectedPackage8Digit, selectedSelectCode, equipmentExist, refreshData]);

    const handleItemDelete = useCallback(async (id: string) => {
        // const id = deleteId;
        // 1. Backup data for rollback
        const prevDisplayData = [...displayData];
        const prevEquipmentList = [...equipmentList];

        // 2. Optimistic UI update
        setDisplayData(prev => prev.filter(item => item.package_selection_code !== id));
        setEditKey(prev => prev.filter(k => k !== id));
        setExpandedAccordions(prev => prev.filter(item => item !== id));

        try {
            // 3. Find related equipment
            const equipment = equipmentExist();
            if (!equipment) {
                throw new Error('Equipment not found');
            }

            // 4. Prepare updated config
            const updatedConfig = equipment.config.map(config => ({
                ...config,
                data_with_selection_code: config.data_with_selection_code.filter(
                    item => item.package_selection_code !== id
                )
            })).filter(config =>
                // Keep config only if it has data or matches current package8digit
                config.data_with_selection_code.length > 0 ||
                config.package8digit === selectedPackage8Digit
            );

            // 5. Decide to update or delete
            // let response;
            if (updatedConfig.length === 0) {
                // Case 1: No more config items - delete entire equipment
                // response = await validate.delete(equipment._id!);

                setDeleteId(equipment._id!);

                setDialogTitle(`Confirm delete validate config: ${selectedEquipmentName}`);
                setDialogMessage(`Are you sure you want to delete?: ${id}`);
                setActionBtnText('DELETE');
                setActionBtnColor('error');

                setOpenDialog(true);

            } else {
                // Case 2: Update equipment with remaining configs
                const updatedEquipment = {
                    ...equipment,
                    config: updatedConfig
                };
                // response = await validate.update(equipment._id!, updatedEquipment);

                // open dialog confirm update
                setUpdateValidateConfig(updatedEquipment);
                setDialogTitle(`Confirm delete validate config: ${selectedEquipmentName}`);
                setDialogMessage(`Are you sure you want to delete?: ${id}`);
                setActionBtnText('UPDATE');
                setActionBtnColor('error');
                setOpenDialog(true);
            }

            // 6. Refresh data
            refreshData();

        } catch (error) {
            // Rollback on error
            setDisplayData(prevDisplayData);
            setEquipmentList(prevEquipmentList);

            setSnackbarSeverity('error');
            setSnackbarMessage(error);
            setOpenSnackbar(true);
        }
    }, [
        displayData,
        equipmentList,
        selectedPackage8Digit,
        selectedEquipmentName,
        equipmentExist,
        refreshData
    ]);

    return (
        <div>
            <Grid2 container spacing={1}>

                <Grid2 size={4}>
                    <Autocomplete
                        id="free-solo-select-equipment"
                        size='small'
                        freeSolo
                        fullWidth
                        options={equipmentList.map((option) => option.equipment_name)}
                        inputValue={selectedEquipmentName}
                        onInputChange={(event, newInputValue) => setSelectedEquipmentName(newInputValue)}
                        renderInput={(params) => <TextField {...params} label="Select Equipment" />}
                    />
                </Grid2>

                <Grid2 size={3}>
                    <Autocomplete
                        id="free-solo-8-digit"
                        size='small'
                        freeSolo
                        fullWidth
                        options={equipmentList
                            .find(item => item.equipment_name === selectedEquipmentName)?.config.map(item => item.package8digit) || []}
                        inputValue={selectedPackage8Digit}
                        onInputChange={(event, newInputValue) => setSelectedPackage8Digit(newInputValue)}
                        renderInput={(params) => <TextField {...params} label="Package 8 Digit" />}
                    />
                </Grid2>

                <Grid2 size={3}>
                    <TextField
                        size='small'
                        fullWidth
                        label="Selection Code"
                        value={selectedSelectCode}
                        select
                        onChange={(e) => setSelectedSelectCode(e.target.value as "1000" | "1001" | "1010" | "1011" | "1100" | "1101" | "1110" | "1111")}
                        disabled={!isNew8Digit}
                    >
                        {['1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111'].map((option) => (
                            <MenuItem key={option} value={option}>
                                {option}
                            </MenuItem>
                        ))}
                    </TextField>
                </Grid2>

                <Grid2 size={2} display="flex" alignItems="center">
                    <Button
                        sx={{ whiteSpace: 'nowrap', overflow: 'hidden' }}
                        variant='outlined'
                        // fullWidth
                        disabled={!canAdd()}
                        onClick={handleAdd}
                    >
                        Add new
                    </Button>
                </Grid2>

                {displayData.map((item) => (
                    <Grid2 key={item.package_selection_code} size={12}>
                        <MemoizedAccordionItem
                            item={item}
                            isEditing={editKey.includes(item.package_selection_code)}
                            isExpanded={expandedAccordions.includes(item.package_selection_code)}
                            onToggle={() => handleItemToggle(item.package_selection_code)}
                            onEdit={() => handleItemEdit(item.package_selection_code)}
                            onSave={(newData) => handleItemSave(item.package_selection_code, newData)}
                            onCancel={() => handleItemCancel(item.package_selection_code)}
                            onDelete={() => handleItemDelete(item.package_selection_code)}
                        />
                    </Grid2>
                ))}
            </Grid2>

            <SnackbarNotify
                open={openSnackbar}
                onClose={() => setOpenSnackbar(false)}
                snackbarSeverity={snackbarSeverity}
                onConfirm={() => setOpenSnackbar(false)}
                message={snackbarMessage}
            />
            <DialogConfirm
                open={openDialog}
                onConfirm={onConfirm}
                onClose={() => setOpenDialog(false)}

                actionBtnText={actionBtnText}
                actionBtnColor={actionBtnColor}
                title={dialogTitle}
                message={dialogMessage}
            />
        </div>
    );
}
