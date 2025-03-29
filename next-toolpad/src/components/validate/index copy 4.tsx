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

    const [selectionState, setSelectionState] = useState<{
        equipmentName: string
        package8Digit: string
        selectionCode: SelectionCode
    }>({
        equipmentName: '',
        package8Digit: '',
        selectionCode: '1000'
    })

    const [displayData, setDisplayData] = useState<DataWithSelectionCode[]>([])
    const [editKeys, setEditKeys] = useState<Set<string>>(new Set())
    const [expandedAccordions, setExpandedAccordions] = useState<Set<string>>(new Set())
    const [editContext, setEditContext] = useState<{
        package8digit: string
        package_selection_code: string
    } | null>(null)

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
            selectionState.selectionCode

        const isCode1000LimitReached = selectionState.selectionCode === '1000' &&
            displayData.length >= 1

        return hasRequiredFields && !isCode1000LimitReached
    }, [selectionState, displayData.length])

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
                if (type === 'equipment') {
                    const equipmentExists = equipmentList.some(e => e.equipment_name === value)
                    return {
                        ...prev,
                        equipmentName: value,
                        package8Digit: equipmentExists ? prev.package8Digit : '',
                        selectionCode: equipmentExists ? prev.selectionCode : '1000'
                    }
                }

                if (type === 'package') {
                    const selectedPackage = currentEquipment?.config.find(c => c.package8digit === value)
                    return {
                        ...prev,
                        package8Digit: value,
                        selectionCode: selectedPackage?.selection_code as SelectionCode || prev.selectionCode
                    }
                }

                if (type === 'code') {
                    return {
                        ...prev,
                        selectionCode: value as SelectionCode
                    }
                }
                return prev
            })
        },
        [equipmentList, currentEquipment]
    )

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
        setEditContext(null)
    }, [])

    const handleEdit = useCallback((pkg: DataWithSelectionCode) => {
        const equipment = equipmentList.find(e => e.equipment_name === selectionState.equipmentName)
        const parentPackage = equipment?.config.find(c =>
            c.data_with_selection_code.some(d => d.package_selection_code === pkg.package_selection_code)
        )

        if (parentPackage) {
            setEditContext({
                package8digit: parentPackage.package8digit,
                package_selection_code: pkg.package_selection_code
            })
        }
        setEditKeys(prev => new Set([...prev, pkg.package_selection_code]))
    }, [equipmentList, selectionState.equipmentName])

    const handleEditSave = useCallback(async (id: string, newData: DataWithSelectionCode) => {
        try {
            // Validation
            if (!newData.package_selection_code.trim() || !newData.product_name.trim()) {
                throw new Error('Please fill all required fields')
            }

            let updatedEquipment: ValidateConfig
            const existingEquipment = equipmentList.find(e => e.equipment_name === selectionState.equipmentName)

            // Case 1: New Equipment
            if (!existingEquipment) {
                updatedEquipment = {
                    equipment_name: selectionState.equipmentName,
                    config: [{
                        package8digit: selectionState.package8Digit,
                        selection_code: selectionState.selectionCode,
                        data_with_selection_code: [newData]
                    }]
                }
                const response = await validate.create(updatedEquipment)
                setEquipmentList(prev => [...prev, response])
            }

            // Case 2: Existing Equipment, New Package
            else if (isNewPackage) {
                updatedEquipment = {
                    ...existingEquipment,
                    config: [
                        ...existingEquipment.config,
                        {
                            package8digit: selectionState.package8Digit,
                            selection_code: selectionState.selectionCode,
                            data_with_selection_code: [newData]
                        }
                    ]
                }
                const response = await validate.update(existingEquipment._id!, updatedEquipment)
                setEquipmentList(prev => prev.map(eq => eq._id === existingEquipment._id ? response : eq))
            }

            // Case 3: Existing Package
            else {
                updatedEquipment = {
                    ...existingEquipment,
                    config: existingEquipment.config.map(config => {
                        if (editContext && config.package8digit !== editContext.package8digit) {
                            return config
                        }
                        return {
                            ...config,
                            data_with_selection_code: config.data_with_selection_code.map(item =>
                                item.package_selection_code === id ? newData : item
                            )
                        }
                    })
                }
                const response = await validate.update(existingEquipment._id!, updatedEquipment)
                setEquipmentList(prev => prev.map(eq => eq._id === existingEquipment._id ? response : eq))
            }

            // Update display data
            setDisplayData(prev => prev.map(item => item.package_selection_code === id ? newData : item))

            setSnackbar({
                open: true,
                message: 'Saved successfully',
                severity: 'success'
            })

        } catch (error) {
            setSnackbar({
                open: true,
                message: handleError(error, 'Failed to save package'),
                severity: 'error'
            })
        } finally {
            setEditKeys(prev => {
                const newSet = new Set(prev)
                newSet.delete(id)
                return newSet
            })
            setEditContext(null)
        }
    }, [equipmentList, selectionState, isNewPackage, editContext, validate])

    const handleEditDelete = useCallback((id: string) => {
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
                const selectedPackage = currentEquipment?.config.find(c => c.package8digit === selectionState.package8Digit)
                setDisplayData(selectedPackage?.data_with_selection_code || [])
            } else if (selectionState.equipmentName) {
                setDisplayData(currentEquipment?.config.flatMap(c => c.data_with_selection_code) || [])
            } else {
                setDisplayData([])
            }
        }

        updateDisplayData()
    }, [selectionState, currentEquipment])

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
                        onEdit={() => handleEdit(pkg)}
                        onSave={(newData) => handleEditSave(pkg.package_selection_code, newData)}
                        onCancel={() => handleEditCancel(pkg.package_selection_code)}
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