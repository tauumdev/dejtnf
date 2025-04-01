'use client'
import React, { Fragment, useCallback, useEffect, useMemo, useState } from 'react'
import { Autocomplete, Button, Grid2, MenuItem, TextField } from '@mui/material'
import { useApiContext } from '@/src/context/apiContext'
import type { ValidateConfig, ConfigItem, DataWithSelectionCode } from './validatePropsType'
import { v4 as uuidv4 } from 'uuid'
import MemoizedAccordionItem from './memoizedAccordionItem'
import { SnackbarNotify } from '../snackbar'
import _, { eq } from 'lodash'

// ==================== Type Definitions ====================
interface User {
    name: string
    email: string
    role: string
}

interface ValidateConfigProps {
    user: User
}

type SelectionCode = "1000" | "1001" | "1010" | "1011" | "1100" | "1101" | "1110" | "1111"

// ==================== Main Component ====================
export default function ValidateConfigComponent({ user }: ValidateConfigProps) {
    // ==================== Context & State ====================
    const { validate } = useApiContext()
    const [equipmentList, setEquipmentList] = useState<ValidateConfig[]>([])

    const [selectionState, setSelectionState] = useState<{
        equipmentName: string
        package8Digit: string
        selectionCode: SelectionCode
        package_selection_code: string
    }>({
        equipmentName: '',
        package8Digit: '',
        selectionCode: '1000',
        package_selection_code: ''
    })

    const [autocompleteOptions, setAutocompleteOptions] = useState<{
        equipment_name: string[];
        package8digit: string[];
        selection_code: SelectionCode[];
        package_selection_code: string[];
    }>({
        equipment_name: [],
        package8digit: [],
        selection_code: [],
        package_selection_code: [],
    })

    const [editKeys, setEditKeys] = useState<Set<string>>(new Set())
    const [expandedAccordions, setExpandedAccordions] = useState<Set<string>>(new Set())

    const [snackbar, setSnackbar] = useState<{
        open: boolean
        message: string
        severity: 'error' | 'info' | 'success' | 'warning'
    }>({
        open: false,
        message: '',
        severity: 'info'
    })

    const [isNew, setIsNew] = useState<boolean>(false);

    // ==================== Derived Values ====================
    const currentEquipment = useMemo(
        () => equipmentList.find(e => e.equipment_name === selectionState.equipmentName),
        [equipmentList, selectionState.equipmentName]
    )

    const packageLength = useMemo(() => {
        const selectedPackage = currentEquipment?.config.find(c => c.package8digit === selectionState.package8Digit);
        if (!selectedPackage) return 0;
        return selectedPackage ? selectedPackage.data_with_selection_code.length : 0;
    }, [currentEquipment, selectionState.package8Digit]);

    const canAddNewPackage = useMemo(() => {
        const hasRequiredFields = selectionState.equipmentName &&
            selectionState.package8Digit &&
            selectionState.selectionCode

        const isCode1000LimitReached = selectionState.selectionCode === '1000' &&
            packageLength >= 1

        return hasRequiredFields && !isCode1000LimitReached
    }, [selectionState, packageLength])

    const equipmentData = useMemo(() => {
        // console.log('Equipment Callback:', selectionState);

        if (!selectionState.equipmentName || !equipmentList?.length) {
            return null;
        }

        // ค้นหา equipment ที่ตรงชื่อ
        const originalEquipment = _.find(equipmentList, {
            equipment_name: selectionState.equipmentName
        });

        if (!originalEquipment) {
            return null;
        }

        // สร้าง deep clone ของ equipment
        const result = _.cloneDeep(originalEquipment);

        // กรอง config ถ้ามี package8Digit
        if (selectionState.package8Digit.length === 8) {
            result.config = _.filter(result.config, {
                package8digit: selectionState.package8Digit
            });
        }

        // กรอง data_with_selection_code ถ้ามี package_selection_code
        if (selectionState.package_selection_code.length === 4) {
            result.config = result.config
                .map(config => ({
                    ...config,
                    data_with_selection_code: _.filter(
                        config.data_with_selection_code,
                        { package_selection_code: selectionState.package_selection_code }
                    )
                }))
                .filter(config => config.data_with_selection_code.length > 0); // กรอง config ที่ว่างออก
        }

        return result;
    }, [selectionState, equipmentList]);

    // ==================== API Handlers ====================
    const fetchEquipmentList = useCallback(async () => {
        try {
            const res = await validate.gets(undefined, undefined, 1, 100, 'equipment_name', 1)
            setEquipmentList(res.docs || [])
            setAutocompleteOptions({
                equipment_name: res.docs.map((e: { equipment_name: string }) => e.equipment_name),
                package8digit: [],
                selection_code: [],
                package_selection_code: []
            })
        } catch (error) {
            console.error('Failed to fetch equipment list:', error)
        }
    }, [])

    const handleSelectionChange = useCallback(
        (type: 'equipment' | 'package' | 'code' | 'package_selection_code', value: string) => {
            setSelectionState(prev => {
                switch (type) {
                    case 'equipment': {
                        const equipmentExists = equipmentList.some(e => e.equipment_name === value);
                        const newPackage8DigitOptions = equipmentExists
                            ? equipmentList.find(e => e.equipment_name === value)?.config.map(c => c.package8digit) || []
                            : [];

                        setAutocompleteOptions(prev => ({
                            ...prev,
                            package8digit: newPackage8DigitOptions,
                            selection_code: [],
                            package_selection_code: []
                        }));

                        setEditKeys(new Set()) // Reset edit keys when equipment changes
                        setExpandedAccordions(new Set()) // Reset expanded accordions when equipment changes
                        return {
                            ...prev,
                            equipmentName: value,
                            package8Digit: '',
                            selectionCode: '1000',
                            package_selection_code: ''
                        };
                    }
                    case 'package': {
                        const selectedPackage = currentEquipment?.config.find(c => c.package8digit === value);
                        const newPackageSelectionCodeOptions = selectedPackage?.data_with_selection_code.map(d => d.package_selection_code) || [];

                        setAutocompleteOptions(prev => ({
                            ...prev,
                            package_selection_code: newPackageSelectionCodeOptions,
                        }));

                        return {
                            ...prev,
                            package8Digit: value,
                            selectionCode: selectedPackage?.selection_code || prev.selectionCode,
                            package_selection_code: ''
                        };
                    }
                    case 'package_selection_code': {
                        const selectedPackage = currentEquipment?.config.find(c => c.data_with_selection_code.some(d => d.package_selection_code === value));
                        return {
                            ...prev,
                            package_selection_code: value,
                        };
                    }
                    case 'code': {
                        return {
                            ...prev,
                            selectionCode: value as SelectionCode // Type assertion
                        };
                    }
                    default:
                        return prev;
                }
            });
        },
        [equipmentList, currentEquipment]
    );

    useEffect(() => {
        fetchEquipmentList()
    }, [fetchEquipmentList])

    const addNewData = useCallback(() => {
        if (!selectionState.equipmentName || !selectionState.package8Digit || !selectionState.selectionCode) return;

        const newData: DataWithSelectionCode = {
            package_selection_code: `NewSelectionCodeuuid${uuidv4()}`,
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

        const existingEquipment = equipmentList.find(e => e.equipment_name === selectionState.equipmentName);

        if (!existingEquipment) {
            console.log('create new equipment:', selectionState.equipmentName);
            setIsNew(true);
            const newEquipment = {
                _id: uuidv4(),
                equipment_name: selectionState.equipmentName,
                config: [{
                    package8digit: selectionState.package8Digit,
                    selection_code: selectionState.selectionCode,
                    data_with_selection_code: [newData]
                }]
            };

            setEquipmentList(prev => [...prev, newEquipment]);

            const itemKey = `${newEquipment._id}|${selectionState.package8Digit}|${newData.package_selection_code}`;
            setEditKeys(prev => new Set([...prev, itemKey]));
            setExpandedAccordions(prev => new Set([...prev, itemKey]));
            return;
        }

        console.log('update equipment:', selectionState.equipmentName);
        setIsNew(false);
        const configItem = existingEquipment.config.find(c => c.package8digit === selectionState.package8Digit);

        if (!configItem) {
            console.log('create new configItem:', selectionState.package8Digit);
            const updatedEquipment = {
                ...existingEquipment,
                config: [
                    ...existingEquipment.config,
                    {
                        package8digit: selectionState.package8Digit,
                        selection_code: selectionState.selectionCode,
                        data_with_selection_code: [newData]
                    }
                ]
            };

            setEquipmentList(prev =>
                prev.map(item =>
                    item.equipment_name === existingEquipment.equipment_name
                        ? updatedEquipment
                        : item
                )
            );
        } else {
            console.log('update configItem where:', selectionState.package8Digit);

            const packageExists = configItem.data_with_selection_code.some(
                d => d.package_selection_code === selectionState.selectionCode
            );

            const productExists = configItem.data_with_selection_code.some(
                d => d.product_name === newData.product_name
            );

            if (!packageExists && !productExists) {
                console.log('create new dataItem:', selectionState.selectionCode);

                const updatedConfig = {
                    ...configItem,
                    data_with_selection_code: [newData, ...configItem.data_with_selection_code]
                };

                setEquipmentList(prev =>
                    prev.map(item =>
                        item.equipment_name === existingEquipment.equipment_name
                            ? {
                                ...item,
                                config: item.config.map(config =>
                                    config.package8digit === configItem.package8digit
                                        ? updatedConfig
                                        : config
                                ),
                            }
                            : item
                    )
                );
            } else {
                console.log('exist package_selection_code or product_name');
                let message = packageExists && productExists
                    ? `Both package_selection_code:${selectionState.selectionCode} and product_name:${newData.product_name} already exist`
                    : packageExists
                        ? `package_selection_code:${selectionState.selectionCode} already exists`
                        : `product_name:${newData.product_name} already exists`;

                setSnackbar({
                    open: true,
                    message,
                    severity: 'error'
                });
                return;
            }
        }

        const itemKey = `${existingEquipment._id}|${selectionState.package8Digit}|${newData.package_selection_code}`;
        setEditKeys(prev => new Set([...prev, itemKey]));
        setExpandedAccordions(prev => new Set([...prev, itemKey]));
    }, [equipmentList, selectionState]);

    const handleSave = useCallback(async (itemKey: string, updatedData: DataWithSelectionCode) => {
        try {
            const [_id, package8digit, package_selection_code] = itemKey.split('|');

            const updatedEquipmentList = equipmentList.map(equip => updateEquipment(equip, _id, package8digit, package_selection_code, updatedData));

            setEquipmentList(updatedEquipmentList);

            const updatedEquipment = updatedEquipmentList.find(e => e._id === _id);
            if (!updatedEquipment) {
                throw new Error('Equipment not found');
            }

            if (isNew) {
                await validate.create(updatedEquipment);
                setIsNew(false);
            } else {
                await validate.update(_id, updatedEquipment);
            }

            updateKeysAndAccordions(itemKey);

            setSnackbar({
                open: true,
                message: 'Save successful',
                severity: 'success'
            });
            fetchEquipmentList();
        } catch (error) {
            handleSaveError(error);
        } finally {
            console.log('Save Finally.');
        }
    }, [equipmentList, isNew, validate, fetchEquipmentList]);

    const handleDelete = useCallback(async (itemKey: string) => {
        const [_id, package8digit, package_selection_code] = itemKey.split('|');

        try {
            const updatedEquipmentList = equipmentList.map(equip => updateEquipment(equip, _id, package8digit, package_selection_code));

            setEquipmentList(updatedEquipmentList);
            const updatedEquipment = updatedEquipmentList.find(e => e._id === _id);
            if (!updatedEquipment) {
                throw new Error('Equipment not found');
            }

            if (updatedEquipment.config.length === 0) {
                await validate.delete(_id);
            } else {
                await validate.update(_id, updatedEquipment);
            }
            updateKeysAndAccordions(itemKey);
            setSnackbar({
                open: true,
                message: `Delete successful`,
                severity: 'success'
            });
            fetchEquipmentList();
        } catch (error) {
            handleSaveError(error);
        } finally {
            console.log('Save Finally.');
        }
    }, [equipmentList, validate, fetchEquipmentList]);

    const updateEquipment = (
        equip: ValidateConfig,
        _id: string,
        package8digit: string,
        package_selection_code: string,
        updatedData: DataWithSelectionCode | null = null
    ): ValidateConfig => {
        if (equip._id !== _id) return equip;

        const updatedConfig = equip.config.map(config => {
            if (config.package8digit !== package8digit) return config;

            const updatedDataList = updatedData
                ? config.data_with_selection_code.map(item =>
                    item.package_selection_code === package_selection_code
                        ? updatedData
                        : item
                )
                : config.data_with_selection_code.filter(item =>
                    item.package_selection_code !== package_selection_code
                );

            return {
                ...config,
                data_with_selection_code: updatedDataList
            };
        }).filter(config =>
            config.data_with_selection_code &&
            config.data_with_selection_code.length > 0
        );

        return {
            ...equip,
            config: updatedConfig
        };
    };

    const updateKeysAndAccordions = (itemKey: string) => {
        setEditKeys(prev => {
            const newSet = new Set(prev);
            newSet.delete(itemKey);
            return newSet;
        });
        setExpandedAccordions(prev => new Set([...prev, itemKey]));
    };

    const handleSaveError = (error: any) => {
        let errorMessage = 'An error occurred while saving data';
        if (error.response) {
            const validationErrors = error.response.data.errors.msg;
            console.log('Error Response:', error.response);
            errorMessage = validationErrors.map((err: { msg: string }) => err.msg).join(', ');
        } else {
            errorMessage = error.message;
        }

        setSnackbar({
            open: true,
            message: errorMessage,
            severity: 'error'
        });
    };

    return (
        <div className="validate-config-container">
            {/* Selection Controls */}
            <Grid2 container spacing={2} sx={{ mb: 3 }}>
                <Grid2 size={4}>
                    <Autocomplete
                        id="equipment-select"
                        size='small'
                        freeSolo
                        options={autocompleteOptions.equipment_name}
                        value={selectionState.equipmentName}
                        onInputChange={(_, value) => handleSelectionChange('equipment', value)}
                        renderInput={(params) => (
                            <TextField {...params} label="Select Equipment" fullWidth />
                        )}
                    />
                </Grid2>

                <Grid2 size={3}>
                    <Autocomplete
                        id="package-select"
                        size='small'
                        freeSolo
                        options={autocompleteOptions.package8digit}
                        value={selectionState.package8Digit}
                        onInputChange={(_, value) => handleSelectionChange('package', value)}
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                label="Package 8 Digit"
                                inputProps={{ ...params.inputProps, maxLength: 8 }}
                            />
                        )}
                    />
                </Grid2>

                <Grid2 size={2}>
                    <TextField
                        size='small'
                        select
                        fullWidth
                        label="Selection Code"
                        value={selectionState.selectionCode}
                        onChange={(e) => handleSelectionChange('code', e.target.value)}
                        disabled={autocompleteOptions.package8digit.some(code => code === selectionState.package8Digit)}
                    >
                        {['1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111'].map(code => (
                            <MenuItem key={code} value={code}>{code}</MenuItem>
                        ))}
                    </TextField>
                </Grid2>

                {user.role === 'admin' &&
                    <Grid2 size={2} display="flex" alignItems="center">
                        <Button
                            variant="outlined"
                            fullWidth
                            disabled={!canAddNewPackage}
                            sx={{ whiteSpace: 'nowrap' }}
                            onClick={() => {
                                addNewData()
                            }}
                        >
                            Add New
                        </Button>
                    </Grid2>
                }
            </Grid2>

            {/* Package List */}
            <div className="package-list">
                {/* <p>{`select state: [${selectionState.equipmentName}], [${selectionState.package8Digit}], [${selectionState.selectionCode}], [${selectionState.package_selection_code}]`}</p>
                <pre>{`exit ${JSON.stringify([...editKeys], null, 2)}`}</pre>
                <pre>{`expended ${JSON.stringify([...expandedAccordions], null, 2)}`}</pre> */}

                {
                    equipmentData && (
                        <>
                            {equipmentData.config.map((config: ConfigItem) => (
                                <Fragment key={config.package8digit}>
                                    {config.data_with_selection_code.map((data: DataWithSelectionCode) => {
                                        const itemKey = `${equipmentData._id}|${config.package8digit}|${data.package_selection_code}`;
                                        return (
                                            <MemoizedAccordionItem
                                                key={itemKey}
                                                userRole={user.role}
                                                item={data}
                                                isEditing={editKeys.has(itemKey)}
                                                isExpanded={expandedAccordions.has(itemKey)}
                                                onToggle={() => {
                                                    setExpandedAccordions(prev => {
                                                        const newSet = new Set(prev);
                                                        if (newSet.has(itemKey)) {
                                                            newSet.delete(itemKey);
                                                        } else {
                                                            newSet.add(itemKey);
                                                        }
                                                        return newSet;
                                                    });
                                                }}
                                                onEdit={() => {
                                                    setEditKeys(prev => new Set([...prev, itemKey]));
                                                }}
                                                onSave={(updatedData) => {
                                                    handleSave(itemKey, updatedData);
                                                }}
                                                onCancel={() => {
                                                    setEditKeys(prev => {
                                                        const newSet = new Set(prev);
                                                        newSet.delete(itemKey);
                                                        return newSet;
                                                    });
                                                }}

                                                onDelete={() => handleDelete(itemKey)}
                                            />
                                        );

                                    })}
                                </Fragment>
                            ))}
                        </>
                    )
                }
            </div>

            {/* Snackbar for notifications */}
            <SnackbarNotify
                open={snackbar.open}
                onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
                snackbarSeverity={snackbar.severity}
                onConfirm={() => setSnackbar(prev => ({ ...prev, open: false }))}
                message={snackbar.message}
            />
        </div >
    )
}

