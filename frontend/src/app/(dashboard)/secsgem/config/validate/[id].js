'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useDejtnfApi } from '../../contexts/DejtnfApiContext';
import { Box, Stack, Typography, Button, Paper, List, ListItem, Container, FormControl, InputLabel, Select, MenuItem, CircularProgress } from '@mui/material';

export default function ConfigPage() {
    const { configs, loading, deleteExistingConfig, createNewConfig, fetchConfigs, getConfigById, updateExistingConfig } = useDejtnfApi();
    const [selectedEquipment, setSelectedEquipment] = useState('');
    const [selectedConfig, setSelectedConfig] = useState(null);
    const router = useRouter();
    const { id } = router.query;

    useEffect(() => {
        if (id) {
            const fetchConfig = async () => {
                const data = await getConfigById(id);
                setSelectedConfig(data);
            };
            fetchConfig();
        }
    }, [id, getConfigById]);

    if (loading) return <CircularProgress />;

    const handleSelectChange = (e) => {
        setSelectedEquipment(e.target.value);
    };

    const handleDelete = async () => {
        await deleteExistingConfig(id);
        router.push('/config');
    };

    const handleSave = async () => {
        if (selectedConfig) {
            await updateExistingConfig(id, selectedConfig);
        } else {
            await createNewConfig(selectedConfig);
        }
        router.push('/config');
    };

    return (
        <Container>
            <Box my={4}>
                <Typography variant="h4" component="h1" gutterBottom>
                    {selectedConfig ? 'Edit Configuration' : 'Create Configuration'}
                </Typography>
                <FormControl fullWidth size="small" margin="normal">
                    <InputLabel>Select Equipment</InputLabel>
                    <Select
                        value={selectedEquipment}
                        onChange={handleSelectChange}
                        label="Select Equipment"
                    >
                        {configs.map((eqs) => (
                            <MenuItem key={eqs._id} value={eqs.config}>
                                {eqs.equipment_name}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
                <Paper elevation={3} sx={{ padding: 2, marginTop: 2 }}>
                    <Typography variant="h6" gutterBottom>
                        Configuration Details
                    </Typography>
                    {selectedConfig && (
                        <List>
                            {selectedConfig.config.map((cfg, index) => (
                                <ListItem key={index}>
                                    <Typography variant="body1">
                                        Package: {cfg.package8digit}
                                    </Typography>
                                    <Typography variant="body1">
                                        Selection Code: {cfg.selection_code}
                                    </Typography>
                                    <Typography variant="body1">
                                        Recipe Name: {cfg.data_with_selection_code[0].recipe_name}
                                    </Typography>
                                    <Typography variant="body1">
                                        Product Name: {cfg.data_with_selection_code[0].product_name}
                                    </Typography>
                                </ListItem>
                            ))}
                        </List>
                    )}
                </Paper>
                <Stack direction="row" spacing={2} mt={2}>
                    <Button variant="contained" color="primary" onClick={handleSave}>
                        Save
                    </Button>
                    {selectedConfig && (
                        <Button variant="contained" color="secondary" onClick={handleDelete}>
                            Delete
                        </Button>
                    )}
                </Stack>
            </Box>
        </Container>
    );
}