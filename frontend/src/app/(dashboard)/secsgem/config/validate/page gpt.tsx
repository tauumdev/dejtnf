'use client'
import React, { useState } from 'react';
import { UseApi } from '../../../../../context/ValidateApiContext';
import {
    Box, Stack, Typography, Button, Paper, List, ListItem, Container,
    FormControl, InputLabel, Select, MenuItem, Divider, Accordion,
    AccordionSummary, AccordionDetails, ListItemText
} from '@mui/material';
import { ExpandMore, Edit, Delete } from '@mui/icons-material';

export default function EquipmentPage() {
    const { configs, loading, deleteConfig } = UseApi();
    const [selectedEquipment, setSelectedEquipment] = useState<string | null>(null);

    if (loading) return <Typography variant="h6">Loading...</Typography>;

    // หา Equipment ที่ถูกเลือก
    const selectedConfig = selectedEquipment ? configs.docs.find(eq => eq._id === selectedEquipment) : null;

    return (
        <Container maxWidth="md" sx={{ py: 4 }}>
            <Typography variant="h4" gutterBottom>Equipment Configuration</Typography>

            {/* Dropdown เลือก Equipment */}
            <FormControl fullWidth size="small" sx={{ mb: 3 }}>
                <InputLabel>Select Equipment</InputLabel>
                <Select
                    value={selectedEquipment || ""}
                    onChange={(e) => setSelectedEquipment(e.target.value)}
                    label="Select Equipment"
                >
                    {configs.docs.map((eq) => (
                        <MenuItem key={eq._id} value={eq._id}>
                            {eq.equipment_name}
                        </MenuItem>
                    ))}
                </Select>
            </FormControl>

            {/* แสดงข้อมูล Equipment */}
            {selectedConfig && (
                <Paper elevation={3} sx={{ p: 3 }}>
                    <Typography variant="h6" gutterBottom>
                        {selectedConfig.equipment_name} Configuration
                    </Typography>
                    <Divider sx={{ mb: 2 }} />

                    <List>
                        {selectedConfig.config.map((cfg, index) => (
                            <ListItem key={index} sx={{ display: 'block' }}>
                                {/* Accordion หลักของแต่ละ Package */}
                                <Accordion>
                                    <AccordionSummary expandIcon={<ExpandMore />}>
                                        <Typography variant="subtitle1" color="primary">
                                            Package: {cfg.package8digit} (Selection Code: {cfg.selection_code})
                                        </Typography>
                                    </AccordionSummary>
                                    <AccordionDetails>
                                        <Stack spacing={1}>
                                            {/* แสดงข้อมูล data_with_selection_code */}
                                            {cfg.data_with_selection_code.map((data, dataIndex) => (
                                                <Accordion key={dataIndex} sx={{ mb: 2 }}>
                                                    <AccordionSummary expandIcon={<ExpandMore />}>
                                                        <Typography variant="body1" color="secondary">
                                                            Package Selection Code: {data.package_selection_code}
                                                        </Typography>
                                                    </AccordionSummary>
                                                    <AccordionDetails>
                                                        <Stack spacing={1} sx={{ pl: 2 }}>
                                                            <Typography variant="body2"><strong>Operation Code:</strong> {data.operation_code}</Typography>
                                                            <Typography variant="body2"><strong>On Operation:</strong> {data.on_operation}</Typography>
                                                            <Typography variant="body2"><strong>Validate Type:</strong> {data.validate_type}</Typography>
                                                            <Typography variant="body2"><strong>Recipe Name:</strong> {data.recipe_name}</Typography>
                                                            <Typography variant="body2"><strong>Product Name:</strong> {data.product_name}</Typography>

                                                            {/* แสดงค่า options แบบไม่ใช้ List */}
                                                            <Typography variant="body2"><strong>Options:</strong></Typography>
                                                            <Typography variant="body2" sx={{ pl: 2 }}>
                                                                - Use Operation Code: {data.options.use_operation_code ? 'Yes' : 'No'}
                                                            </Typography>
                                                            <Typography variant="body2" sx={{ pl: 2 }}>
                                                                - Use On Operation: {data.options.use_on_operation ? 'Yes' : 'No'}
                                                            </Typography>
                                                            <Typography variant="body2" sx={{ pl: 2 }}>
                                                                - Use Lot Hold: {data.options.use_lot_hold ? 'Yes' : 'No'}
                                                            </Typography>
                                                            {/* แสดงค่า allow_tool_id */}
                                                            <Typography variant="body2"><strong>Allow Tool ID:</strong></Typography>
                                                            {Object.entries(data.allow_tool_id).map(([position, tools]) => (
                                                                <Typography key={position} variant="body2" sx={{ pl: 2 }}>
                                                                    {position}: {tools.join(', ')}
                                                                </Typography>
                                                            ))}
                                                        </Stack>
                                                    </AccordionDetails>
                                                </Accordion>
                                            ))}
                                        </Stack>
                                    </AccordionDetails>
                                </Accordion>
                            </ListItem>
                        ))}
                    </List>

                    {/* ปุ่ม Edit / Delete */}
                    <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                        <Button variant="contained" color="primary" startIcon={<Edit />}>
                            Edit
                        </Button>
                        <Button
                            variant="contained"
                            color="error"
                            startIcon={<Delete />}
                            onClick={() => deleteConfig(selectedConfig._id)}
                        >
                            Delete
                        </Button>
                    </Box>
                </Paper>
            )}
        </Container>
    );
}
