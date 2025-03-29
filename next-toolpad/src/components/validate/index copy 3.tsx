'use client'
import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { Autocomplete, Button, Grid2, MenuItem, TextField } from '@mui/material'
import { useApiContext } from '@/src/context/apiContext'
import type { ValidateConfig, ConfigItem, DataWithSelectionCode } from './validatePropsType'
import { v4 as uuidv4 } from 'uuid'
import MemoizedAccordionItem from './memoizedAccordionItem'
import { SnackbarNotify } from '../snackbar'

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

    // Combined state for better organization
    const [selectionState, setSelectionState] = useState<{
        equipmentName: string
        package8Digit: string
        selectionCode: SelectionCode
    }>({
        equipmentName: '',
        package8Digit: '',
        selectionCode: '1000'
    })

    // const [isNew, setIsNew] = useState<{ equipment: ValidateConfig, package: DataWithSelectionCode }>()

    const [displayData, setDisplayData] = useState<DataWithSelectionCode[]>([])
    const [editKeys, setEditKeys] = useState<Set<string>>(new Set())
    const [expandedAccordions, setExpandedAccordions] = useState<Set<string>>(new Set())

    // เพิ่ม State สำหรับเก็บข้อมูลที่กำลังแก้ไข
    const [editContext, setEditContext] = useState<{
        package8digit: string;
        package_selection_code: string;
    } | null>(null);


    const [snackbar, setSnackbar] = useState<{
        open: boolean
        message: string
        severity: 'error' | 'info' | 'success' | 'warning'
    }>({
        open: false,
        message: '',
        severity: 'info'
    })

    // ==================== Derived Values ====================
    const currentEquipment = useMemo(
        () => equipmentList.find(e => e.equipment_name === selectionState.equipmentName),
        [equipmentList, selectionState.equipmentName]
    )

    const currentPackage = useMemo(
        () => currentEquipment?.config.find(c => c.package8digit === selectionState.package8Digit),
        [currentEquipment, selectionState.package8Digit]
    )


    const canAddNewPackage = useMemo(() => {
        const hasRequiredFields = selectionState.equipmentName &&
            selectionState.package8Digit &&
            selectionState.selectionCode;

        const isCode1000LimitReached = selectionState.selectionCode === '1000' &&
            displayData.length >= 1;

        return hasRequiredFields && !isCode1000LimitReached;
    }, [selectionState, displayData.length]);

    const isNewEquipment = !currentEquipment
    const isNewPackage = !currentPackage

    // ==================== API Handlers ====================
    const fetchEquipmentList = useCallback(async () => {
        try {
            const res = await validate.gets(undefined, undefined, 1, 100, 'equipment_name', 1)
            setEquipmentList(res.docs || [])
        } catch (error) {
            console.error('Failed to fetch equipment list:', error)
        }
    }, [])


    const handleSelectionChange = useCallback(
        (type: 'equipment' | 'package' | 'code', value: string) => {

            setSelectionState(prev => {

                // กรณีเปลี่ยน Equipment
                if (type === 'equipment') {
                    const equipmentExists = equipmentList.some(e => e.equipment_name === value);

                    return {
                        ...prev,
                        equipmentName: value,
                        // ถ้าไม่มี Equipment นี้ในลิสต์ ให้ reset package8Digit ด้วย
                        package8Digit: equipmentExists ? prev.package8Digit : '',
                        selectionCode: equipmentExists ? prev.selectionCode : '1000'
                    };
                }

                // กรณีเปลี่ยน Package
                if (type === 'package') {
                    const selectedPackage = currentEquipment?.config.find(c => c.package8digit === value);
                    return {
                        ...prev,
                        package8Digit: value,
                        selectionCode: selectedPackage?.selection_code || prev.selectionCode
                    };
                }

                // กรณีเปลี่ยน Selection Code
                if (type === 'code') {
                    return {
                        ...prev,
                        selectionCode: value as SelectionCode // Type assertion
                    };
                }
                return prev;
            });
        },
        [equipmentList, currentEquipment]
    );

    const handleAddNewPackage = useCallback(() => {
        const newPackage: DataWithSelectionCode = {
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
        }

        setDisplayData(prev => [newPackage, ...prev])
        setExpandedAccordions(prev => new Set([...prev, newPackage.package_selection_code]))
        setEditKeys(prev => new Set([...prev, newPackage.package_selection_code]))
    }, [])


    const handleEditCancel = useCallback((id: string) => {
        setEditKeys(prev => {
            const newSet = new Set(prev)
            newSet.delete(id)
            return newSet
        })
    }, []);


    // ปรับฟังก์ชันเมื่อกด Edit
    const handleEdit = useCallback((pkg: DataWithSelectionCode) => {
        // หา Package ที่เป็น parent ของ Item นี้
        const equipment = equipmentList.find(e => e.equipment_name === selectionState.equipmentName);
        const parentPackage = equipment?.config.find(c =>
            c.data_with_selection_code.some(d => d.package_selection_code === pkg.package_selection_code)
        );

        if (parentPackage) {
            setEditContext({
                package8digit: parentPackage.package8digit,
                package_selection_code: pkg.package_selection_code
            });
            setEditKeys(prev => new Set([...prev, pkg.package_selection_code]));
        }
    }, [equipmentList, selectionState.equipmentName]);


    // ปรับฟังก์ชัน handleEditSave
    // const handleEditSave = useCallback(async (id: string, newData: DataWithSelectionCode) => {
    //     console.log('Saving item with ID:', id, 'New Data:', newData);

    //     try {
    //         // Validation
    //         if (!newData.package_selection_code.trim() || !newData.product_name.trim()) {
    //             setSnackbar({
    //                 open: true,
    //                 message: 'Please fill all required fields',
    //                 severity: 'error'
    //             });
    //             return;
    //         }

    //         // หา Equipment และ Config ที่เกี่ยวข้อง
    //         const equipment = equipmentList.find(e => e.equipment_name === selectionState.equipmentName);
    //         if (!equipment) throw new Error('Equipment not found');


    //         // สร้าง Equipment ใหม่พร้อมข้อมูลที่อัปเดต
    //         const updatedEquipment = {
    //             ...equipment,
    //             config: equipment.config.map(config => {
    //                 // กรองเฉพาะ Config ที่เกี่ยวข้อง (ใช้จาก editContext)
    //                 if (editContext && config.package8digit !== editContext.package8digit) {
    //                     return config;
    //                 }

    //                 return {
    //                     ...config,
    //                     data_with_selection_code: config.data_with_selection_code.map(item =>
    //                         item.package_selection_code === id ? newData : item
    //                     )
    //                 };
    //             })

    //         };
    //         console.log('Updated Equipment:', updatedEquipment);


    //         // Optimistic UI Update
    //         setDisplayData(prev =>
    //             prev.map(item => item.package_selection_code === id ? newData : item)
    //         );

    //         // Call API
    //         const response = await validate.update(equipment._id!, updatedEquipment);

    //         console.log('API response:', response);

    //         // Update State
    //         setEquipmentList(prev =>
    //             prev.map(eq => eq._id === equipment._id ? response : eq)
    //         );

    //         setSnackbar({
    //             open: true,
    //             message: 'Saved successfully',
    //             severity: 'success'
    //         });

    //     } catch (error) {
    //         setSnackbar({
    //             open: true,
    //             message: handleError(error, 'Failed to save package'),
    //             severity: 'error'
    //         });
    //     } finally {
    //         setEditKeys(prev => {
    //             const newSet = new Set(prev);
    //             newSet.delete(id);
    //             return newSet;
    //         });
    //         setEditContext(null);
    //     }
    // }, [equipmentList, selectionState.equipmentName, editContext, validate]);

    const handleEditSave = useCallback(async (id: string, newData: DataWithSelectionCode) => {
        try {
            // Validation
            if (!newData.package_selection_code.trim() || !newData.product_name.trim()) {
                throw new Error('Please fill all required fields');
            }

            // หา Equipment ที่เกี่ยวข้อง
            let equipment = equipmentList.find(e => e.equipment_name === selectionState.equipmentName);
            const isNewEquipment = !equipment;

            // กรณีสร้าง Equipment ใหม่
            if (isNewEquipment) {
                equipment = {
                    equipment_name: selectionState.equipmentName,
                    config: [{
                        package8digit: selectionState.package8Digit,
                        selection_code: selectionState.selectionCode,
                        data_with_selection_code: [newData]
                    }]
                };
            }
            // กรณีเพิ่ม Package ใหม่
            else if (isNewPackage) {
                equipment = {
                    ...equipment,
                    config: [
                        ...equipment.config,
                        {
                            package8digit: selectionState.package8Digit,
                            selection_code: selectionState.selectionCode,
                            data_with_selection_code: [newData]
                        }
                    ]
                };
            }
            // กรณีอัปเดตข้อมูลที่มีอยู่
            else {
                equipment = {
                    ...equipment,
                    config: equipment.config.map(config => {
                        // ใช้ editContext เพื่อหา Package ที่ถูกต้อง
                        if (editContext && config.package8digit !== editContext.package8digit) {
                            return config;
                        }

                        return {
                            ...config,
                            data_with_selection_code: config.data_with_selection_code.map(item =>
                                item.package_selection_code === id ? newData : item
                            )
                        };
                    })
                };
            }

            // Optimistic UI Update
            setDisplayData(prev =>
                prev.map(item => item.package_selection_code === id ? newData : item)
            );

            // Call API
            const response = isNewEquipment
                ? await validate.create(equipment)
                : await validate.update(equipment._id!, equipment);

            // Update State
            setEquipmentList(prev =>
                isNewEquipment
                    ? [...prev, response]
                    : prev.map(eq => eq._id === equipment!._id ? response : eq)
            );

            setSnackbar({
                open: true,
                message: 'Saved successfully',
                severity: 'success'
            });

        } catch (error) {
            setSnackbar({
                open: true,
                message: handleError(error, 'Failed to save package'),
                severity: 'error'
            });
        } finally {
            setEditKeys(prev => {
                const newSet = new Set(prev);
                newSet.delete(id);
                return newSet;
            });
            setEditContext(null);
        }
    }, [equipmentList, selectionState, isNewPackage, editContext, validate]);

    const handleEditDelete = useCallback((id: string) => {
        console.log('Deleting item with ID:', id);

        setDisplayData(prev => prev.filter(item => item.package_selection_code !== id))
        setEditKeys(prev => {
            const newSet = new Set(prev)
            newSet.delete(id)
            return newSet
        })
    }, [])

    // ==================== Effect Hooks ====================
    useEffect(() => {
        fetchEquipmentList()
    }, [fetchEquipmentList])

    useEffect(() => {
        const updateDisplayData = () => {
            if (selectionState.package8Digit.length === 8) {
                const selectedPackage = currentEquipment?.config.find(c => c.package8digit === selectionState.package8Digit);
                setDisplayData(selectedPackage?.data_with_selection_code || []);
            } else if (selectionState.equipmentName) {
                setDisplayData(currentEquipment?.config.flatMap(c => c.data_with_selection_code) || []);
            } else {
                setDisplayData([]);
            }
        }

        updateDisplayData();
    }, [selectionState, currentEquipment]);

    return (
        <div className="validate-config-container">
            {/* Selection Controls */}
            <Grid2 container spacing={2} sx={{ mb: 3 }}>
                <Grid2 size={4}>
                    <Autocomplete
                        id="equipment-select"
                        size='small'
                        freeSolo
                        options={equipmentList.map(e => e.equipment_name)}
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
                        options={currentEquipment?.config.map(c => c.package8digit) || []}
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
                        disabled={!isNewPackage}
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
                            onClick={handleAddNewPackage}
                        >
                            Add New
                        </Button>
                    </Grid2>
                }
            </Grid2>

            {/* Package List */}
            <div className="package-list">
                {displayData.map(pkg => (
                    <MemoizedAccordionItem
                        userRole={user.role}
                        key={pkg.package_selection_code}
                        item={pkg}
                        isEditing={editKeys.has(pkg.package_selection_code)}
                        isExpanded={expandedAccordions.has(pkg.package_selection_code)}
                        onToggle={() => setExpandedAccordions(prev => {
                            const newSet = new Set(prev)
                            newSet.has(pkg.package_selection_code)
                                ? newSet.delete(pkg.package_selection_code)
                                : newSet.add(pkg.package_selection_code)
                            return newSet
                        })}
                        onEdit={() => {
                            // เรียก handleEdit เพื่อตั้งค่า editContext ก่อน
                            handleEdit(pkg);
                            // แล้วจึงตั้งค่า editKeys
                            setEditKeys(prev => new Set([...prev, pkg.package_selection_code]));
                        }}
                        onSave={(newData) => handleEditSave(pkg.package_selection_code, newData)}
                        onCancel={() => {
                            handleEditCancel(pkg.package_selection_code);
                            setEditContext(null); // เคลียร์ editContext เมื่อยกเลิก
                        }}
                        onDelete={() => handleEditDelete(pkg.package_selection_code)}
                    />
                ))}
            </div>

            {/* Snackbar for notifications */}
            <SnackbarNotify
                open={snackbar.open}
                onClose={() => setSnackbar(prev => ({ ...prev, open: false }))}
                snackbarSeverity={snackbar.severity}
                onConfirm={() => setSnackbar(prev => ({ ...prev, open: false }))}
                message={snackbar.message}
            />
        </div>
    )
}