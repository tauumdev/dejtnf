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

// ==================== Utility Functions ====================
const handleError = (error: unknown, defaultMessage: string): string => {
    if (Array.isArray(error)) {
        return error.map(err => `${err.param || 'field'}: ${err.msg || 'Invalid value'}`).join(', ')
    }

    if (error instanceof Error) {
        return error.message
    }

    if (typeof error === 'string') {
        return error
    }

    return defaultMessage
}

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

    const equipmentData = useMemo(() => {
        console.log('Equipment Callback:', selectionState);

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

    const addNewData = useCallback(() => {
        if (!selectionState.equipmentName || !selectionState.package8Digit || !selectionState.selectionCode) return;

        const newData: DataWithSelectionCode = {
            package_selection_code: `NewSelectionCode,${uuidv4()}`,
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

        // Find existing equipment
        const existingEquipment = equipmentList.find(e => e.equipment_name === selectionState.equipmentName);

        if (!existingEquipment) {
            console.log('create new equipment:', selectionState.equipmentName);
            setIsNew(true)
            const newEquipment: ValidateConfig = {
                _id: uuidv4(),
                equipment_name: selectionState.equipmentName,
                config: [{
                    package8digit: selectionState.package8Digit,
                    selection_code: selectionState.selectionCode,
                    data_with_selection_code: [newData]
                }]
            };

            setEquipmentList(prev => [...prev, newEquipment]);

            // สร้าง itemKey จาก equipment ใหม่
            const itemKey = `${newEquipment._id},${selectionState.package8Digit},${newData.package_selection_code}`;
            setEditKeys(prev => new Set([...prev, itemKey]));
            setExpandedAccordions(prev => new Set([...prev, itemKey]));
            return;
        }

        console.log('update equipment:', selectionState.equipmentName);
        setIsNew(false)
        // Find or create config item
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

            // Check for duplicates
            const packageExists = configItem.data_with_selection_code.some(
                d => d.package_selection_code === selectionState.package_selection_code
            );

            const productExists = configItem.data_with_selection_code.some(
                d => d.product_name === newData.product_name
            );

            if (!packageExists && !productExists) {
                console.log('create new dataItem:', selectionState.package_selection_code);

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
                    ? `Both package_selection_code:${selectionState.package_selection_code} and product_name:${newData.product_name} already exist`
                    : packageExists
                        ? `package_selection_code:${selectionState.package_selection_code} already exists`
                        : `product_name:${newData.product_name} already exists`;

                setSnackbar({
                    open: true,
                    message,
                    severity: 'error'
                });
                return;
            }
        }

        // สร้าง itemKey จาก equipment ที่มีอยู่
        const itemKey = `${existingEquipment._id},${selectionState.package8Digit},${newData.package_selection_code}`;
        setEditKeys(prev => new Set([...prev, itemKey]));
        setExpandedAccordions(prev => new Set([...prev, itemKey]));
    }, [equipmentList, selectionState]);

    const handleSave = useCallback((itemKey: string) => {
        const [_id, package8digit, package_selection_code] = itemKey.split(',');
        // console.log(_id, package8digit, package_selection_code);
        // console.log(equipmentList.find(e => e._id));

        const equipmentSave = equipmentList.find(e => e._id === _id);
        if (isNew) {
            console.log('new equipmentSave:', equipmentSave);
            // if (equipmentSave) {
            //     validate.create(equipmentSave);
            // } else {
            //     console.error('equipmentSave is undefined');
            // }
        } else {
            console.log('update equipmentSave:', equipmentSave);
            // if (equipmentSave) {
            //     validate.update(_id, equipmentSave);
            // } else {
            //     console.error('equipmentSave is undefined');
            // }
        }

    }, [equipmentList, isNew])

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

                <Grid2 size={3}>
                    <TextField
                        size='small'
                        select
                        fullWidth
                        label="Selection Code"
                        value={selectionState.selectionCode}
                        onChange={(e) => handleSelectionChange('code', e.target.value)}
                    // disabled={!isNewPackage}
                    >
                        {['1000', '1001', '1010', '1011', '1100', '1101', '1110', '1111'].map(code => (
                            <MenuItem key={code} value={code}>{code}</MenuItem>
                        ))}
                    </TextField>
                </Grid2>

                <Grid2 size={4}>
                    <Autocomplete
                        id="package-select"
                        size="small"
                        freeSolo
                        options={autocompleteOptions.package_selection_code}
                        value={selectionState.package_selection_code}
                        onInputChange={(_, value) => handleSelectionChange('package_selection_code', value)}
                        renderInput={(params) => (
                            <TextField
                                {...params}
                                label="Package With Selection Code"
                            />
                        )}
                    />
                </Grid2>

                {user.role === 'admin' &&
                    <Grid2 size={3} display="flex" alignItems="center">
                        <Button
                            variant="outlined"
                            fullWidth
                            disabled={!canAddNewPackage}
                            // onClick={handleAddNewPackage}
                            onClick={() => {
                                // console.log('Add New Package:', selectionState);
                                addNewData()
                                // create add new package logic here

                            }}
                        >
                            Add New
                        </Button>
                    </Grid2>
                }
            </Grid2>

            {/* Package List */}
            <div className="package-list">
                <p>{`select state: [${selectionState.equipmentName}], [${selectionState.package8Digit}], [${selectionState.selectionCode}], [${selectionState.package_selection_code}]`}</p>
                <pre>{`exit ${JSON.stringify([...editKeys], null, 2)}`}</pre>
                <pre>{`expended ${JSON.stringify([...expandedAccordions], null, 2)}`}</pre>

                {
                    equipmentData && (
                        <>
                            {equipmentData.config.map((config: ConfigItem) => (
                                <Fragment key={config.package8digit}>
                                    {config.data_with_selection_code.map((data: DataWithSelectionCode) => {
                                        const itemKey = `${equipmentData._id},${config.package8digit},${data.package_selection_code}`;
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
                                                    // Handle save logic

                                                    setEquipmentList(prev =>
                                                        prev.map(equip =>
                                                            equip.equipment_name === equipmentData?.equipment_name
                                                                ? {
                                                                    ...equip,
                                                                    config: equip.config.map(config =>
                                                                        config.package8digit === config.package8digit
                                                                            ? {
                                                                                ...config,
                                                                                data_with_selection_code: config.data_with_selection_code.map(item =>
                                                                                    item.package_selection_code === data.package_selection_code
                                                                                        ? updatedData
                                                                                        : item
                                                                                )
                                                                            }
                                                                            : config
                                                                    )
                                                                }
                                                                : equip
                                                        )
                                                    );
                                                    handleSave(itemKey);
                                                    setEditKeys(prev => {
                                                        const newSet = new Set(prev);
                                                        newSet.delete(itemKey);
                                                        return newSet;
                                                    });

                                                }}
                                                onCancel={() => {
                                                    setEditKeys(prev => {
                                                        const newSet = new Set(prev);
                                                        newSet.delete(itemKey);
                                                        return newSet;
                                                    });
                                                }}
                                                onDelete={() => {
                                                    setEquipmentList(prev =>
                                                        prev.map(equip =>
                                                            equip.equipment_name === equipmentData?.equipment_name
                                                                ? {
                                                                    ...equip,
                                                                    config: equip.config.map(config =>
                                                                        config.package8digit === config.package8digit
                                                                            ? {
                                                                                ...config,
                                                                                data_with_selection_code: config.data_with_selection_code.filter(
                                                                                    item => item.package_selection_code !== data.package_selection_code
                                                                                )
                                                                            }
                                                                            : config
                                                                    )
                                                                }
                                                                : equip
                                                        )
                                                    );
                                                    setEditKeys(prev => {
                                                        const newSet = new Set(prev);
                                                        newSet.delete(itemKey);
                                                        return newSet;
                                                    });
                                                    setExpandedAccordions(prev => {
                                                        const newSet = new Set(prev);
                                                        newSet.delete(itemKey);
                                                        return newSet;
                                                    });
                                                }}
                                            />
                                        );

                                    })}
                                </Fragment>
                            ))}
                        </>
                    )
                }
            </div>

            {equipmentList?.map((equipment: ValidateConfig) =>
                <div key={equipment._id}>
                    <li >{equipment.equipment_name}</li>
                    {equipment.config.map((config: ConfigItem) =>
                        <div key={config.package8digit} style={{ paddingLeft: '20px' }}>
                            <li>{config.package8digit}</li>
                            {config.data_with_selection_code.map((data: DataWithSelectionCode) =>
                                <div key={data.package_selection_code} style={{ paddingLeft: '20px' }}>
                                    <li>{data.product_name}</li>
                                </div>
                            )}
                        </div>
                    )}

                </div>
            )}

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

