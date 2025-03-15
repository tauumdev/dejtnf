// DataValidationForm.tsx
import { Box, TextField, FormControlLabel, Checkbox, Typography, Grid, MenuItem } from '@mui/material';
import React, { useRef } from 'react';

interface DataValidationFormProps {
    dataItem: any; // Replace 'any' with the appropriate type for your data
    editedData: any; // Replace 'any' with the appropriate type for your edited data
    setEditedData: (data: any) => void; // Replace 'any' with the appropriate type for your edited data
    isEditing: boolean;
}

const DataValidationForm: React.FC<DataValidationFormProps> = ({ dataItem, editedData, setEditedData, isEditing }) => {
    const inputRef = useRef<HTMLInputElement | null>(null);
    return (
        <Grid container spacing={2}>
            {/* แถวที่ 1 */}
            <Grid item xs={12} sm={4}>
                <TextField
                    inputRef={inputRef}
                    label="Product Name"
                    value={isEditing ? editedData.product_name : dataItem.product_name}
                    onChange={(e) => setEditedData({ ...editedData, product_name: e.target.value })}
                    size="small"
                    fullWidth
                    disabled={!isEditing}
                />
            </Grid>
            <Grid item xs={12} sm={4}>
                <TextField
                    inputRef={inputRef}
                    label="Package With Selection Code"
                    value={isEditing ? editedData.package_selection_code : dataItem.package_selection_code}
                    onChange={(e) => setEditedData({ ...editedData, package_selection_code: e.target.value })}
                    size="small"
                    fullWidth
                    disabled={!isEditing}
                />
            </Grid>
            <Grid item xs={12} sm={4}>
                {/* <TextField
                    inputRef={inputRef}
                    label="Validate Type"
                    value={isEditing ? editedData.validate_type : dataItem.validate_type}
                    onChange={(e) => setEditedData({ ...editedData, validate_type: e.target.value })}
                    size="small"
                    fullWidth
                    disabled={!isEditing}
                /> */}
                {isEditing ?
                    (
                        <TextField
                            select
                            size='small'
                            fullWidth
                            label="Validate Type"
                            value={editedData.validate_type}
                            onChange={(e) => setEditedData({ ...editedData, validate_type: e.target.value })}
                        >
                            <MenuItem value="recipe" > Recipe </MenuItem>
                            <MenuItem value="tool_id" > Tool Id </MenuItem>

                        </TextField>
                    ) : (
                        <TextField
                            label="Validate Type"
                            value={isEditing ? editedData.validate_type : dataItem.validate_type}
                            size="small"
                            fullWidth
                            disabled={!isEditing}
                        />
                    )
                }
            </Grid>

            {/* แถวที่ 2 */}
            <Grid item xs={12} sm={4}>
                <TextField
                    inputRef={inputRef}
                    label="Recipe Name"
                    value={isEditing ? editedData.recipe_name : dataItem.recipe_name}
                    onChange={(e) => setEditedData({ ...editedData, recipe_name: e.target.value })}
                    size="small"
                    fullWidth
                    disabled={!isEditing}
                />
            </Grid>
            <Grid item xs={12} sm={4}>
                <TextField
                    inputRef={inputRef}
                    label="Operation Code"
                    value={isEditing ? editedData.operation_code : dataItem.operation_code}
                    onChange={(e) => setEditedData({ ...editedData, operation_code: e.target.value })}
                    size="small"
                    fullWidth
                    disabled={!isEditing}
                />
            </Grid>
            <Grid item xs={12} sm={4}>
                <TextField
                    inputRef={inputRef}
                    label="On Operation"
                    value={isEditing ? editedData.on_operation : dataItem.on_operation}
                    onChange={(e) => setEditedData({ ...editedData, on_operation: e.target.value })}
                    size="small"
                    fullWidth
                    disabled={!isEditing}
                />
            </Grid>

            {/* แถวที่ 3 - Checkboxes */}
            <Grid item xs={12} sm={4}>
                <FormControlLabel
                    control={
                        <Checkbox
                            checked={isEditing ? editedData.options.use_operation_code : dataItem.options.use_operation_code}
                            onChange={(e) => setEditedData({ ...editedData, options: { ...editedData.options, use_operation_code: e.target.checked } })}
                            size="small"
                            disabled={!isEditing}
                        />
                    }
                    label={<Typography variant='body2'>Check Operation Code</Typography>}
                />
            </Grid>
            <Grid item xs={12} sm={4}>
                <FormControlLabel
                    control={
                        <Checkbox
                            checked={isEditing ? editedData.options.use_on_operation : dataItem.options.use_on_operation}
                            onChange={(e) => setEditedData({ ...editedData, options: { ...editedData.options, use_on_operation: e.target.checked } })}
                            size="small"
                            disabled={!isEditing}
                        />
                    }
                    label={<Typography variant='body2'>Check On Operation</Typography>}
                />
            </Grid>
            <Grid item xs={12} sm={4}>
                <FormControlLabel
                    control={
                        <Checkbox
                            checked={isEditing ? editedData.options.use_lot_hold : dataItem.options.use_lot_hold}
                            onChange={(e) => setEditedData({ ...editedData, options: { ...editedData.options, use_lot_hold: e.target.checked } })}
                            size="small"
                            disabled={!isEditing}
                        />
                    }
                    label={<Typography variant='body2'>Check Lot Hold</Typography>}
                />
            </Grid>

            {/* แถวที่ 4 - Allow Tool ID */}
            <Grid item xs={12}>
                <Typography variant="body2" sx={{ pb: 2 }}>
                    Allow Tool ID
                </Typography>
                <Grid container spacing={2}>
                    {Object.entries(dataItem.allow_tool_id).map(([position, tools], index) => (
                        <Grid item xs={12} sm={6} key={position}>
                            <TextField
                                inputRef={inputRef}
                                label={position.replace('_', ' ').toUpperCase()}
                                value={isEditing ? editedData.allow_tool_id[position].join(', ') : tools.join(', ')}
                                onChange={(e) => setEditedData({
                                    ...editedData,
                                    allow_tool_id: {
                                        ...editedData.allow_tool_id,
                                        [position]: e.target.value.split(',').map(tool => tool.trim()).filter(tool => tool !== '').map(tool => tool.replace(/\s*,\s*/g, ','))
                                    }
                                })}
                                size="small"
                                fullWidth

                                disabled={!isEditing}
                            />
                        </Grid>
                    ))}
                </Grid>

            </Grid>

        </Grid>
    )
}

export default DataValidationForm;