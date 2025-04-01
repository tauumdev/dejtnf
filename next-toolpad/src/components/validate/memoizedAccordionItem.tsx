import React, { useState, useEffect, useCallback } from 'react';
import { Accordion, AccordionSummary, AccordionDetails, Button, TextField, Tooltip, Typography, useTheme, Grid2, MenuItem, FormGroup, Box, FormControlLabel, Checkbox } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import isEqual from 'lodash/isEqual';
import { DataWithSelectionCode, Options, AllowToolId } from './validatePropsType';
import { DialogConfirm } from '../dialogConfirm';

type OptionConfig = {
    key: keyof Options;
    label: string;
}

const optionsConfig: OptionConfig[] = [
    { key: 'use_operation_code', label: 'Use Operation Code' },
    { key: 'use_on_operation', label: 'Use On Operation' },
    { key: 'use_lot_hold', label: 'Use Lot Hold' },
] as const;

type PositionsConfig = {
    key: keyof AllowToolId;
    label: string;
}

const positionsConfig: PositionsConfig[] = [
    { key: 'position_1', label: 'Position 1' },
    { key: 'position_2', label: 'Position 2' },
    { key: 'position_3', label: 'Position 3' },
    { key: 'position_4', label: 'Position 4' },
] as const;

type MemoizedAccordionItemProps = {
    userRole: string;
    item: DataWithSelectionCode;
    isEditing: boolean;
    isExpanded: boolean;
    onToggle: () => void;
    onEdit: () => void;
    onSave: (newData: DataWithSelectionCode) => void;
    onCancel: () => void;
    onDelete: () => void;
};

const MemoizedAccordionItem = React.memo(
    ({
        userRole,
        item,
        isEditing,
        isExpanded,
        onToggle,
        onEdit,
        onSave,
        onCancel,
        onDelete,
    }: MemoizedAccordionItemProps) => {
        const [localData, setLocalData] = useState<DataWithSelectionCode>(item);
        const theme = useTheme();

        const [dialog, setDialog] = useState<{
            title: string,
            message: string,
            confirmText: 'CREATE' | 'DELETE' | 'UPDATE' | 'SAVE' | 'OK';
            confirmColor: "success" | "error" | "info" | "warning" | "primary" | "secondary" | "inherit",
            cancelText: string,
            open: boolean,
            onConfirm?: () => void; // เพิ่มส่วนนี้เพื่อให้สามารถเรียกใช้ callback ได้
        }
        >({
            title: '',
            message: '',
            confirmText: 'OK',
            confirmColor: 'primary',
            cancelText: 'Cancel',
            open: false,
            onConfirm: undefined // ค่าเริ่มต้นเป็น undefined
        })

        useEffect(() => {
            setLocalData(item);
        }, [item]);

        const handleFieldChange = useCallback(
            (field: keyof DataWithSelectionCode | `options.${keyof Options}` | `allow_tool_id.${keyof AllowToolId}`,
                value: string | string[] | boolean) => {
                if (field.startsWith('options.')) {
                    const optionKey = field.replace('options.', '') as keyof typeof localData.options;
                    setLocalData(prev => ({
                        ...prev,
                        options: {
                            ...prev.options,
                            [optionKey]: value as boolean
                        }
                    }));
                } else if (field.startsWith('allow_tool_id.')) {
                    const positionKey = field.replace('allow_tool_id.', '') as keyof AllowToolId;
                    setLocalData(prev => ({
                        ...prev,
                        allow_tool_id: {
                            ...prev.allow_tool_id,
                            [positionKey]: typeof value === 'string' ? value.split(',') : value
                        }
                    }));
                } else {
                    setLocalData(prev => ({
                        ...prev,
                        [field]: value as string
                    }));
                }
            },
            []
        );

        const handleSaveClick = useCallback(() => {
            const cleanedData = {
                ...localData,
                package_selection_code: localData.package_selection_code.trim(),
                product_name: localData.product_name.trim(),
            };

            if (!cleanedData.package_selection_code || !cleanedData.product_name) {
                setDialog({
                    title: 'Validation Error',
                    message: 'Please fill all required fields',
                    confirmText: 'OK',
                    confirmColor: 'error',
                    cancelText: '',
                    open: true,
                });
                return;
            }

            // แสดง Dialog ยืนยันก่อน Save
            setDialog({
                title: 'Confirm Save',
                message: `Are you sure you want to save:${cleanedData.product_name}?`,
                confirmText: 'SAVE',
                confirmColor: 'success',
                cancelText: 'Cancel',
                open: true,
                onConfirm: () => onSave(cleanedData) // เพิ่ม callback สำหรับการยืนยัน
            });
        }, [localData, onSave]);

        const handleDeleteClick = useCallback(() => {
            // แสดง Dialog ยืนยันก่อน Delete
            setDialog({
                title: 'Confirm Delete',
                message: `Are you sure you want to delete:${localData.product_name}?`,
                confirmText: 'DELETE',
                confirmColor: 'error',
                cancelText: 'Cancel',
                open: true,
                onConfirm: onDelete // เพิ่ม callback สำหรับการยืนยัน
            });
        }, [localData, onDelete]);

        const DialogConfirmWithProps = useCallback(() => (
            <DialogConfirm
                title={dialog.title}
                message={dialog.message}
                confirmText={dialog.confirmText}
                confirmColor={dialog.confirmColor}
                cancelText={dialog.cancelText}
                open={dialog.open}
                onCancel={() => setDialog(prev => ({ ...prev, open: false }))}
                onConfirm={() => {
                    setDialog(prev => ({ ...prev, open: false }));
                    // @ts-ignore
                    dialog.onConfirm?.();
                }}
            />
        ), [dialog]);

        return (
            <>
                <Accordion expanded={isExpanded} onChange={onToggle}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography color={isEditing ? theme.palette.secondary.main : theme.palette.primary.main}>
                            {isEditing ? localData.product_name : item.product_name}
                        </Typography>
                    </AccordionSummary>
                    <AccordionDetails>
                        <Grid2 container spacing={2}>
                            {/* Package Selection Code */}
                            <Grid2 size={4}>
                                {isEditing ? (
                                    <TextField
                                        fullWidth
                                        size="small"
                                        label="Package Selection Code"
                                        value={localData.package_selection_code.split('uuid')[0]}
                                        onChange={(e) => handleFieldChange('package_selection_code', e.target.value)}
                                    />
                                ) : (
                                    <TextField
                                        fullWidth
                                        size='small'
                                        label="Package Selection Code"
                                        value={item.package_selection_code.split('uuid')[0]}
                                    />
                                )}
                            </Grid2>
                            {/* Product Name */}
                            <Grid2 size={4}>
                                {isEditing ? (
                                    <TextField
                                        fullWidth
                                        size="small"
                                        label="Product Name"
                                        value={localData.product_name}
                                        onChange={(e) => handleFieldChange('product_name', e.target.value)}
                                    />
                                ) : (
                                    <TextField
                                        fullWidth
                                        size='small'
                                        label="Product Name"
                                        value={item.product_name}
                                    />
                                )}
                            </Grid2>
                            {/* Validate Type */}
                            <Grid2 size={4}>
                                {isEditing ? (
                                    <TextField
                                        fullWidth
                                        size="small"
                                        autoComplete='off'
                                        label="Validate Type"
                                        select
                                        value={localData.validate_type}
                                        onChange={(e) => handleFieldChange('validate_type', e.target.value)}
                                    >
                                        <MenuItem value="recipe">Recipe</MenuItem>
                                        <MenuItem value="tool_id">Tool ID</MenuItem>
                                    </TextField>
                                ) : (
                                    <TextField
                                        fullWidth
                                        size='small'
                                        label="Validate Type"
                                        value={item.validate_type === 'recipe' ? 'Recipe' : 'Tool ID'}
                                    />
                                )}
                            </Grid2>
                            {/* Recipe Name */}
                            <Grid2 size={4}>
                                {isEditing ? (
                                    <TextField
                                        fullWidth
                                        size="small"
                                        autoComplete='off'
                                        label="Recipe Name"
                                        value={localData.recipe_name}
                                        onChange={(e) => handleFieldChange('recipe_name', e.target.value)}
                                    />
                                ) : (
                                    <TextField
                                        fullWidth
                                        size='small'
                                        label="Recipe Name"
                                        value={item.recipe_name}
                                    />
                                )}
                            </Grid2>
                            {/* Operation Cod */}
                            <Grid2 size={4}>
                                {isEditing ? (
                                    <TextField
                                        fullWidth
                                        size="small"
                                        autoComplete='off'
                                        label="Operation Code"
                                        value={localData.operation_code}
                                        onChange={(e) => handleFieldChange('operation_code', e.target.value)}
                                    />
                                ) : (
                                    <TextField
                                        fullWidth
                                        size='small'
                                        label="Operation Code"
                                        value={item.operation_code}
                                    />
                                )}
                            </Grid2>
                            {/* On Operation */}
                            <Grid2 size={4}>
                                {isEditing ? (
                                    <TextField
                                        fullWidth
                                        size="small"
                                        autoComplete='off'
                                        label="On Operation"
                                        value={localData.on_operation}
                                        onChange={(e) => handleFieldChange('on_operation', e.target.value)}
                                    />
                                ) : (
                                    <TextField
                                        fullWidth
                                        size='small'
                                        label="On Operation"
                                        value={item.on_operation}
                                    />
                                )}
                            </Grid2>

                            {/* options check box */}
                            <Grid2 size={12}>
                                <FormGroup>
                                    <Box display="flex" flexDirection="row" flexWrap="wrap" gap={3}>
                                        {optionsConfig.map(opt => (
                                            <FormControlLabel
                                                key={opt.key}
                                                control={
                                                    <Checkbox
                                                        checked={isEditing ? localData.options[opt.key] : item.options[opt.key]}
                                                        onChange={(e) => handleFieldChange(`options.${opt.key}`, e.target.checked)}
                                                    />
                                                }
                                                label={opt.label}
                                            />
                                        ))}
                                    </Box>
                                </FormGroup>
                            </Grid2>

                            {/* Allow tool ids */}
                            <Grid2 size={12}>
                                <Typography>Allow Tool IDs</Typography>
                            </Grid2>

                            {/* Positions */}
                            {positionsConfig.map(pos => (
                                <Grid2 key={pos.key} size={6}>
                                    {isEditing ? (
                                        <TextField
                                            size="small"
                                            autoComplete='off'
                                            label={pos.label}
                                            value={localData.allow_tool_id[pos.key].join(',')}
                                            onChange={(e) => handleFieldChange(
                                                `allow_tool_id.${pos.key}`,
                                                e.target.value
                                            )}
                                            fullWidth
                                        />
                                    ) : (
                                        <TextField
                                            size="small"
                                            label={pos.label}
                                            value={localData.allow_tool_id[pos.key].join(', ')}
                                            fullWidth
                                            InputProps={{
                                                readOnly: true,
                                            }}
                                        />
                                    )}
                                </Grid2>
                            ))}

                            {/* Actions button */}
                            {userRole === 'admin' &&
                                <Grid2 size={12} display="flex" justifyContent="flex-end" gap={1}>
                                    {isEditing ? (
                                        <>
                                            <Button variant="outlined" size="small" color="inherit" onClick={onCancel}>
                                                Cancel
                                            </Button>
                                            <Button variant="outlined" size="small" color="success" onClick={handleSaveClick}>
                                                Save
                                            </Button>
                                        </>
                                    ) : (
                                        <>
                                            <Button variant="outlined" size="small" onClick={onEdit}>
                                                Edit
                                            </Button>
                                            <Button variant="outlined" size="small" color="error" onClick={handleDeleteClick}>
                                                Delete
                                            </Button>
                                        </>
                                    )}
                                </Grid2>
                            }
                        </Grid2>
                    </AccordionDetails>
                </Accordion>

                <DialogConfirmWithProps />
            </>
        );
    },
    (prevProps, nextProps) =>
        isEqual(prevProps.item, nextProps.item) &&
        prevProps.isEditing === nextProps.isEditing &&
        prevProps.isExpanded === nextProps.isExpanded
);

MemoizedAccordionItem.displayName = 'MemoizedAccordionItem';

export default MemoizedAccordionItem;
