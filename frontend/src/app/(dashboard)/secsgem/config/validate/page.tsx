'use client'
import React, { useState } from 'react';
import { Box, Stack, Typography, Paper, Container, FormControl, InputLabel, Select, MenuItem, Divider, Avatar, Accordion, AccordionSummary, AccordionDetails, Card } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { UseApi } from '../../../../../context/ValidateApiContext';

export default function EquipmentConfigPage() {
    const { configs, loading } = UseApi();
    const [selectedEquipment, setSelectedEquipment] = useState(null);

    if (loading) return <Typography>Loading...</Typography>;

    const selectedConfig = selectedEquipment ? configs.docs.find(eq => eq.config === selectedEquipment) : null;

    return (
        <Container maxWidth="lg" sx={{ my: 4 }}>
            {/* Header */}
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'medium', textAlign: 'center', mb: 4 }}>
                Equipment Configuration
            </Typography>

            {/* Equipment Selector */}
            <FormControl fullWidth size="small" sx={{ mb: 4 }}>
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

            {/* Equipment Details */}
            {selectedConfig && (
                <Paper elevation={0} sx={{ p: 3, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
                    <Stack spacing={3}>
                        {/* Equipment Header */}
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Avatar sx={{ bgcolor: 'primary.main', width: 48, height: 48 }}>
                                {selectedConfig.equipment_name.charAt(0)}
                            </Avatar>
                            <Typography variant="h5" component="h2" sx={{ fontWeight: 'medium' }}>
                                {selectedConfig.equipment_name}
                            </Typography>
                        </Box>

                        {/* <Divider sx={{ borderColor: 'divider' }} /> */}

                        {/* Configuration Details */}
                        {selectedConfig.config.map((cfg, index) => (
                            <Accordion key={index} elevation={0} sx={{ mb: 2 }}>
                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                    <Typography variant="subtitle1" sx={{ fontWeight: 'medium', fontSize: '0.9rem' }}>
                                        Package: {cfg.package8digit} | Selection Code: {cfg.selection_code}
                                    </Typography>
                                </AccordionSummary>
                                <AccordionDetails>
                                    <Stack spacing={2}>
                                        {/* Data with Selection Code */}
                                        {cfg.data_with_selection_code.map((data, dataIndex) => (
                                            <Accordion key={dataIndex} elevation={0} sx={{ mb: 2 }}>
                                                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                                                    <Typography variant="subtitle2" sx={{ fontWeight: 'medium', fontSize: '0.85rem' }}>
                                                        Package Selection Code: {data.package_selection_code}
                                                    </Typography>
                                                </AccordionSummary>
                                                <AccordionDetails>
                                                    <Stack spacing={2}>

                                                        {/* Operation Details */}
                                                        <Card variant="outlined" sx={{ p: 2, backgroundColor: 'background.paper' }}>
                                                            <Typography variant="subtitle2" sx={{ fontWeight: 'medium', mb: 1, fontSize: '0.85rem' }}>
                                                                Config Details
                                                            </Typography>
                                                            <Divider sx={{ mb: 1 }} />
                                                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                                                Operation Code: {data.operation_code}
                                                            </Typography>
                                                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                                                On Operation: {data.on_operation}
                                                            </Typography>
                                                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                                                Validate Type: {data.validate_type}
                                                            </Typography>

                                                            {/* Recipe and Product */}
                                                            <Divider sx={{ mb: 1 }} />
                                                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                                                Recipe Name: {data.recipe_name}
                                                            </Typography>
                                                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                                                Product Name: {data.product_name}
                                                            </Typography>

                                                            {/* Options */}
                                                            <Divider sx={{ mb: 1 }} />
                                                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                                                Use Operation Code: {data.options.use_operation_code ? 'Yes' : 'No'}
                                                            </Typography>
                                                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                                                Use On Operation: {data.options.use_on_operation ? 'Yes' : 'No'}
                                                            </Typography>
                                                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                                                Use Lot Hold: {data.options.use_lot_hold ? 'Yes' : 'No'}
                                                            </Typography>
                                                        </Card>

                                                        {/* Recipe and Product */}
                                                        {/* <Card variant="outlined" sx={{ p: 2, backgroundColor: 'background.paper' }}>
                                                            <Typography variant="subtitle2" sx={{ fontWeight: 'medium', mb: 1, fontSize: '0.85rem' }}>
                                                                Recipe & Product
                                                            </Typography>
                                                            <Divider sx={{ mb: 1 }} />
                                                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                                                Recipe Name: {data.recipe_name}
                                                            </Typography>
                                                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                                                Product Name: {data.product_name}
                                                            </Typography>
                                                        </Card> */}

                                                        {/* Options */}
                                                        {/* <Card variant="outlined" sx={{ p: 2, backgroundColor: 'background.paper' }}>
                                                            <Typography variant="subtitle2" sx={{ fontWeight: 'medium', mb: 1, fontSize: '0.85rem' }}>
                                                                Options
                                                            </Typography>
                                                            <Divider sx={{ mb: 1 }} />
                                                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                                                Use Operation Code: {data.options.use_operation_code ? 'Yes' : 'No'}
                                                            </Typography>
                                                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                                                Use On Operation: {data.options.use_on_operation ? 'Yes' : 'No'}
                                                            </Typography>
                                                            <Typography variant="body2" sx={{ fontSize: '0.8rem' }}>
                                                                Use Lot Hold: {data.options.use_lot_hold ? 'Yes' : 'No'}
                                                            </Typography>
                                                        </Card> */}

                                                        <Card variant="outlined" sx={{ p: 2, backgroundColor: 'background.paper' }}>
                                                            <Typography variant="subtitle2" sx={{ fontWeight: 'medium', mb: 1, fontSize: '0.85rem' }}>
                                                                Allow Tool ID
                                                            </Typography>
                                                            <Divider sx={{ mb: 1 }} />
                                                            {Object.entries(data.allow_tool_id).map(([position, tools]) => (
                                                                // <Box key={position} sx={{ mb: 1 }}>
                                                                <Typography key={position} variant="body2" sx={{ fontWeight: 'medium', fontSize: '0.8rem' }}>
                                                                    {position}: {tools.join(', ')}
                                                                </Typography>
                                                                // </Box>
                                                            ))}
                                                        </Card>

                                                    </Stack>
                                                </AccordionDetails>
                                            </Accordion>
                                        ))}
                                    </Stack>
                                </AccordionDetails>
                            </Accordion>
                        ))}
                    </Stack>
                </Paper>
            )}
        </Container>
    );
}
