'use client'
import React, { useState } from 'react'
import { UseApi } from '../../../../../context/ValidateApiContext';
import { Box, Stack, Typography, Button, Paper, List, ListItem, Container, FormControl, InputLabel, Select, MenuItem } from '@mui/material';


function details(config) {
    return (
        <Box>
            <Typography variant="subtitle1">Package: {config.package8digit}</Typography>
            <Typography variant="body1">Selection Code: {config.selection_code}</Typography>
            {config.data_with_selection_code.map((data, index) => (
                <Box key={index}>
                    <Typography variant="body2">Options:</Typography>
                    <Typography variant="body2">- Use Operation Code: {data.options.use_operation_code ? 'Yes' : 'No'}</Typography>
                    <Typography variant="body2">- Use On Operation: {data.options.use_on_operation ? 'Yes' : 'No'}</Typography>
                    <Typography variant="body2">- Use Lot Hold: {data.options.use_lot_hold ? 'Yes' : 'No'}</Typography>
                    <Typography variant="body2">Operation Code: {data.operation_code}</Typography>
                    <Typography variant="body2">On Operation: {data.on_operation}</Typography>
                    <Typography variant="body2">Validate Type: {data.validate_type}</Typography>
                    <Typography variant="body2">Recipe Name: {data.recipe_name}</Typography>
                    <Typography variant="body2">Product Name: {data.product_name}</Typography>
                    <Typography variant="body2">Allow Tool ID:</Typography>
                    {Object.entries(data.allow_tool_id).map(([position, tools]) => (
                        <Typography key={position} variant="body2">
                            {position}: {tools.join(', ')}
                        </Typography>
                    ))}
                </Box>
            ))}
        </Box>
    )
}


export default function Page() {
    const { configs, loading, deleteConfig, createConfig, fetchConfigs, getConfigById, updateConfig } = UseApi();
    const [selectedEquipment, setSelectedEquipment] = useState(null);

    if (loading) return <p>Loading...</p>;

    const selectedConfig = selectedEquipment ? configs.docs.find(eq => eq.config === selectedEquipment) : null;

    return (
        <Container>
            <Box sx={{ my: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Equipment Configuration
                </Typography>
                <FormControl fullWidth size="small" sx={{ mb: 3 }}>
                    <InputLabel>Select Equipment</InputLabel>
                    <Select
                        value={selectedEquipment || ''}
                        onChange={(e) => setSelectedEquipment(e.target.value)}
                        label="Select Equipment"
                    >
                        {configs.docs.map((eq) => (
                            <MenuItem key={eq._id} value={eq.config}>
                                {eq.equipment_name}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>

                {selectedConfig && (
                    <Paper elevation={3} sx={{ p: 3 }}>
                        <Typography variant="h6" gutterBottom>
                            {selectedConfig.equipment_name} Configuration
                        </Typography>
                        <List>
                            {selectedConfig.config.map((cfg, index) => (
                                <ListItem key={index}>
                                    <Stack spacing={2} sx={{ width: '100%' }}>
                                        <Typography variant="subtitle1">Package: {cfg.package8digit}</Typography>
                                        <Typography variant="body1">Selection Code: {cfg.selection_code}</Typography>
                                        {cfg.data_with_selection_code.map((data, dataIndex) => (
                                            <Box key={dataIndex} sx={{ pl: 2 }}>
                                                <Typography variant="body2">Options:</Typography>
                                                <Typography variant="body2">- Use Operation Code: {data.options.use_operation_code ? 'Yes' : 'No'}</Typography>
                                                <Typography variant="body2">- Use On Operation: {data.options.use_on_operation ? 'Yes' : 'No'}</Typography>
                                                <Typography variant="body2">- Use Lot Hold: {data.options.use_lot_hold ? 'Yes' : 'No'}</Typography>
                                                <Typography variant="body2">Operation Code: {data.operation_code}</Typography>
                                                <Typography variant="body2">On Operation: {data.on_operation}</Typography>
                                                <Typography variant="body2">Validate Type: {data.validate_type}</Typography>
                                                <Typography variant="body2">Recipe Name: {data.recipe_name}</Typography>
                                                <Typography variant="body2">Product Name: {data.product_name}</Typography>
                                                <Typography variant="body2">Allow Tool ID:</Typography>
                                                {Object.entries(data.allow_tool_id).map(([position, tools]) => (
                                                    <Typography key={position} variant="body2" sx={{ pl: 2 }}>
                                                        {position}: {tools.join(', ')}
                                                    </Typography>
                                                ))}
                                            </Box>
                                        ))}
                                    </Stack>
                                </ListItem>
                            ))}
                        </List>
                        <Box sx={{ mt: 2 }}>
                            <Button variant="contained" color="primary" sx={{ mr: 2 }}>
                                Edit
                            </Button>
                            <Button variant="contained" color="secondary" onClick={() => deleteConfig(selectedConfig._id)}>
                                Delete
                            </Button>
                        </Box>
                    </Paper>
                )}
            </Box>
        </Container>
    );
}