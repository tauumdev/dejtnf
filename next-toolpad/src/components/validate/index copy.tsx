'use client'
import React, { Fragment, useCallback, useEffect, useMemo, useState } from 'react'
import { Autocomplete, Button, Grid2, MenuItem, TextField, Typography } from '@mui/material'
import { useApiContext } from '@/src/context/apiContext'
import { Binary4Digit, ConfigItem, DataWithSelectionCode, ValidateConfig } from './configManager'
import { Add } from '@mui/icons-material'
import { v4 as uuidv4 } from 'uuid'
import MemoizedAccordionItem from './memoizedAccordionItem'

// ==================== Type Definitions ====================
interface User {
    name: string
    email: string
    role: string
}

interface ValidateConfigProps {
    user: User
}

// ==================== Main Component ====================
export default function ValidateConfigComponent({ user }: ValidateConfigProps) {
    // ==================== Context & State ====================
    const { validate } = useApiContext()
    const [equipmentList, setEquipmentList] = useState<ValidateConfig[]>([])

    const [selectionState, setSelectionState] = useState<{
        equipmentName: string
        package8Digit: string
        selectionCode: Binary4Digit
    }>({
        equipmentName: '',
        package8Digit: '',
        selectionCode: '1000',
    })

    const [autocompleteOptions, setAutocompleteOptions] = useState<{
        equipment_name: string[];
        package8digit: string[];
        selection_code: Binary4Digit
    }>({
        equipment_name: [],
        package8digit: [],
        selection_code: '1000',
    })

    const [editKeys, setEditKeys] = useState<Set<string>>(new Set())
    const [addNewKeys, setAddNewKeys] = useState<Set<string>>(new Set())
    const [expandedAccordions, setExpandedAccordions] = useState<Set<string>>(new Set())

    // ==================== API Handlers ====================
    const fetchEquipmentList = useCallback(async () => {
        try {
            const res = await validate.gets(undefined, undefined, 1, 100, 'equipment_name', 1)
            setEquipmentList(res.docs || [])
            setAutocompleteOptions({
                equipment_name: res.docs.map((e: { equipment_name: string }) => e.equipment_name),
                package8digit: [],
                selection_code: '1000',
            })
        } catch (error) {
            console.error('Failed to fetch equipment list:', error)
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [])

    useEffect(() => {
        fetchEquipmentList();
    }, [fetchEquipmentList]); // ✅ Add fetchEquipmentList as dependency

    const equipmentMap = useMemo(() => {
        return new Map(equipmentList.map(e => [e.equipment_name, e]));
    }, [equipmentList]);

    const equipmentDataFilter = useMemo(() => {
        if (!selectionState.equipmentName) return equipmentList;

        // Find equipment that matches the selected equipment name
        const equipment = equipmentMap.get(selectionState.equipmentName);
        if (!equipment) return [];

        // If package8Digit is provided and is 8 characters long, filter configs by package8Digit
        if (selectionState.package8Digit?.length === 8) {
            const config = equipment.config.find(c => c.package8digit === selectionState.package8Digit);
            if (!config) return [];

            // Return a new object without modifying the original data
            return [{ ...equipment, config: [config] }];
        }

        return [equipment];
    }, [selectionState, equipmentList, equipmentMap]);

    // Memoized value to count the number of 'data_with_selection_code' for the selected package
    const dataWithSelectionCodeCount = useMemo(() => {
        const selectedEquipment = equipmentMap.get(selectionState.equipmentName);

        if (selectedEquipment) {
            // Find the selected config for the chosen package8digit
            const selectedConfig = selectedEquipment.config.find(c => c.package8digit === selectionState.package8Digit);

            // Return the length of 'data_with_selection_code' if config exists, otherwise return 0
            return selectedConfig ? selectedConfig.data_with_selection_code.length : 0;
        }

        // Return 0 if no equipment or config is selected
        return 0;
    }, [selectionState.equipmentName, selectionState.package8Digit, equipmentMap]);

    // Memoized value to determine if the "Add New Package" button should be enabled
    const canAddNewPackage = useMemo(() => {
        const hasRequiredFields = selectionState.equipmentName &&
            selectionState.package8Digit &&
            selectionState.selectionCode

        // Check if selection code is '1000' and if the limit for data_with_selection_code is reached
        const isCode1000LimitReached = selectionState.selectionCode === '1000' &&
            dataWithSelectionCodeCount >= 1

        // Return true if all required fields are filled and the limit is not reached
        return hasRequiredFields && !isCode1000LimitReached
    }, [selectionState, dataWithSelectionCodeCount])

    const disableSelectionCode = useMemo(() => {
        return autocompleteOptions.package8digit.some(c => c === selectionState.package8Digit) || addNewKeys.size > 0
    }, [autocompleteOptions.package8digit, selectionState.package8Digit, addNewKeys.size])

    const updateAutocompleteOptions = useCallback((equipmentName: string) => {
        const selectedEquipment = equipmentMap.get(equipmentName);
        setAutocompleteOptions(prev => ({
            ...prev,
            package8digit: selectedEquipment ? selectedEquipment.config.map(c => c.package8digit) : []
        }));
    }, [equipmentMap]);

    // Function to get selectionCode for a given package8digit
    const getSelectionCodeForPackage = useCallback((equipmentName: string, package8Digit: string) => {
        const selectedEquipment = equipmentList.find(e => e.equipment_name === equipmentName);
        if (!selectedEquipment) return '1000'; // Fallback if equipment is not found

        const selectedPackage = selectedEquipment.config.find(c => c.package8digit === package8Digit);
        return selectedPackage ? selectedPackage.selection_code : '1000'; // Fallback to '1000' if package is not found
    }, [equipmentList]);

    const handleSelectionChange = useCallback((type: 'equipment' | 'package' | 'code', value: string) => {
        setSelectionState(prev => {
            switch (type) {
                case 'equipment': {
                    updateAutocompleteOptions(value); // ✅ Use memoized function
                    return {
                        ...prev,
                        equipmentName: value,
                        package8Digit: '',
                        selectionCode: '1000' as Binary4Digit,
                    }
                }
                case 'package': {
                    const selectionCode = getSelectionCodeForPackage(prev.equipmentName, value); // Get selection code based on package
                    return {
                        ...prev,
                        equipmentName: prev.equipmentName,
                        package8Digit: value,
                        selectionCode: selectionCode as Binary4Digit,
                    }
                }
                case 'code': {
                    return {
                        ...prev,
                        equipmentName: prev.equipmentName,
                        package8Digit: prev.package8Digit,
                        selectionCode: value as Binary4Digit,
                    }
                }
                default:
                    return prev;
            }
        })

    }, [updateAutocompleteOptions, getSelectionCodeForPackage])

    const handleAddDataWithSelectionCode = useCallback(() => {
        if (!selectionState.equipmentName || !selectionState.package8Digit || !selectionState.selectionCode) return;

        const initialData: DataWithSelectionCode = {
            package_selection_code: `NewSelectionCodeuuid${uuidv4()}`,
            product_name: 'New Product',
            validate_type: 'recipe',
            recipe_name: '',
            operation_code: '',
            on_operation: '',
            options: { use_operation_code: true, use_on_operation: true, use_lot_hold: true },
            allow_tool_id: { position_1: [], position_2: [], position_3: [], position_4: [] }
        }

        // Step 1: Check if the equipment already exists
        const existEquipment = equipmentMap.get(selectionState.equipmentName);
        // console.log(existEquipment);

        if (!existEquipment) {
            // Create new ValidateConfig
            console.log('Creating new ValidateConfig...');
            const newEquipment: ValidateConfig = {
                _id: `equipmentuuid${uuidv4()}`,
                equipment_name: selectionState.equipmentName,
                config: [
                    {
                        package8digit: selectionState.package8Digit,
                        selection_code: selectionState.selectionCode,
                        data_with_selection_code: [initialData] // Add the initial data here
                    }
                ]
            };

            // Add the new equipment to the list
            setEquipmentList((prev) => [...prev, newEquipment]);

            // Add itemKey to editKeys
            const itemKey = `${newEquipment._id}|${selectionState.package8Digit}|${initialData.package_selection_code}`;
            setEditKeys(prev => new Set([...prev, itemKey]));
            setAddNewKeys(prev => new Set([...prev, itemKey]));
            setExpandedAccordions(prev => new Set([...prev, itemKey]));
            console.log('New equipment added:', newEquipment);

        } else {
            // Step 2: Check if the selected package8digit exists
            const existPackage = existEquipment.config.find(config => config.package8digit === selectionState.package8Digit);

            if (!existPackage) {
                // Create new ConfigItem for this package8digit
                console.log('Creating new ConfigItem...');
                const newConfigItem: ConfigItem = {
                    package8digit: selectionState.package8Digit,
                    selection_code: selectionState.selectionCode,
                    data_with_selection_code: [initialData] // Add the initial data here
                };

                // Add the new config to the equipment's config
                existEquipment.config.push(newConfigItem);

                // Update the equipment list with the updated equipment
                setEquipmentList(prev => [...prev.map(e => ({ ...e }))]);

                // Add itemKey to editKeys
                const itemKey = `${existEquipment._id}|${selectionState.package8Digit}|${initialData.package_selection_code}`;
                setEditKeys(prev => new Set([...prev, itemKey]));
                setAddNewKeys(prev => new Set([...prev, itemKey]));
                setExpandedAccordions(prev => new Set([...prev, itemKey]));
                console.log('New ConfigItem added:', newConfigItem);

            } else {
                // Step 3: Check if the data_with_selection_code exists
                const existData = existPackage.data_with_selection_code.find(data => data.package_selection_code === selectionState.selectionCode);

                if (!existData) {
                    // Create new DataWithSelectionCode
                    console.log('Creating new DataWithSelectionCode...');
                    // Add new data to the existing config's data_with_selection_code array
                    existPackage.data_with_selection_code.unshift(initialData);

                    // Update the equipment list with the updated equipment
                    setEquipmentList(prev => [...prev]);

                    // Add itemKey to editKeys
                    const itemKey = `${existEquipment._id}|${selectionState.package8Digit}|${initialData.package_selection_code}`;
                    setEditKeys(prev => new Set([...prev, itemKey]));
                    setAddNewKeys(prev => new Set([...prev, itemKey]));
                    setExpandedAccordions(prev => new Set([...prev, itemKey]));

                    console.log('New DataWithSelectionCode added:', initialData);
                }
            }
        }
    }, [selectionState, equipmentMap]);

    const handleCancel = useCallback((itemKey: string) => {
        const [_id, package8digit, package_selection_code] = itemKey.split('|');

        const isNewKey: boolean = addNewKeys.has(itemKey);

        if (isNewKey) {
            // Step 1: Remove the added item from equipmentList
            setEquipmentList(prevList => {
                return prevList
                    .map(equipment => {
                        if (equipment._id === _id) {
                            // Create a new copy of config array
                            const updatedConfigs = equipment.config
                                .map(config => {
                                    if (config.package8digit === package8digit) {
                                        // Create a new copy of data_with_selection_code
                                        const updatedData = config.data_with_selection_code.filter(data => data.package_selection_code !== package_selection_code);

                                        return { ...config, data_with_selection_code: updatedData };
                                    }
                                    return config;
                                })
                                .filter(config => config.data_with_selection_code.length > 0); // Remove empty config items

                            return { ...equipment, config: updatedConfigs };
                        }
                        return equipment;
                    })
                    .filter(equipment => equipment.config.length > 0); // Remove empty equipment
            });

            // Step 2: Remove the key from addNewKeys
            setAddNewKeys(prev => {
                const newSet = new Set(prev);
                newSet.delete(itemKey);
                return newSet;
            });
        }

        // Step 3: Remove the itemKey from editKeys (the set of items in edit mode)
        setEditKeys(prevEditKeys => {
            const updatedEditKeys = new Set(prevEditKeys);
            updatedEditKeys.delete(itemKey);
            return updatedEditKeys;
        });

        console.log(`Cancelled and removed: ${itemKey}`);
    }, [addNewKeys, setEquipmentList]);

    return (
        <div className="validate-config-container">
            <pre>{JSON.stringify(selectionState, null, 2)}</pre>
            <pre>{`add new ${JSON.stringify([...addNewKeys], null, 2)}`}</pre>
            <pre>{`edit ${JSON.stringify([...editKeys], null, 2)}`}</pre>
            <pre>{`expend ${JSON.stringify([...expandedAccordions], null, 2)}`}</pre>

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
                        disabled={addNewKeys.size > 0}
                        renderInput={(params) => (
                            <TextField {...params} label="Select Equipment" fullWidth
                                inputProps={{ ...params.inputProps, maxLength: 15 }} />
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
                        disabled={addNewKeys.size > 0}
                        renderInput={(params) => (
                            <TextField
                                {...params} label="Package 8 Digit" fullWidth
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
                        disabled={disableSelectionCode}
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
                            sx={{ whiteSpace: 'nowrap' }}
                            disabled={!canAddNewPackage}
                            onClick={handleAddDataWithSelectionCode}
                            startIcon={<Add />}
                        >
                            Add New
                        </Button>
                    </Grid2>
                }
            </Grid2>

            <div id='equipment-list'>
                {equipmentDataFilter &&
                    equipmentDataFilter.map((eq) =>
                        <Fragment key={eq.equipment_name}>
                            {/* <li>{eq.equipment_name}</li> */}
                            {/* <Typography sx={{ p: 2 }}>{eq.equipment_name}</Typography> */}
                            {eq.config.map((config) => (
                                config.data_with_selection_code.map((data) => {
                                    const itemKey = `${eq._id}|${config.package8digit}|${data.package_selection_code}`;

                                    return (
                                        <MemoizedAccordionItem
                                            key={data.package_selection_code}
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
                                            onSave={(updatedData: DataWithSelectionCode) => console.log(updatedData)}
                                            onCancel={() => handleCancel(itemKey)}
                                            onDelete={() => console.log('delete', itemKey)}
                                        />
                                    )
                                })

                            ))}
                        </Fragment>
                    )}
            </div>
        </div>
    )
}
