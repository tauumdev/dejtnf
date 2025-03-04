'use client';
import React, { useEffect, useState } from 'react';
import { useMqtt } from '../../../../context/MqttContext';
import { Alert, Box, Button, Divider, MenuItem, TextField, Typography, Paper, Grid, Card, CardContent } from '@mui/material';
import { useApiContext } from '../../../../context/apiContext';
import { Equipment } from '@/src/service/types';

export default function EquipmentMonitor() {
    const { connectionStatus, subscribeTopic, unsubscribeTopic } = useMqtt();
    const [selectedEquipment, setSelectedEquipment] = useState('TNF-61'); // Default equipment
    const { equipment } = useApiContext();

    const [equipment_id, setEquipment_id] = useState<Equipment>();

    const [equipmentStatus, setEquipmentStatus] = useState<{
        communicationState: string;
        controlState: string;
        processState: string;
        processProgram: string;
    }>({
        communicationState: 'Unknown',
        controlState: 'Unknown',
        processState: 'Unknown',
        processProgram: 'Unknown'
    });

    useEffect(() => {
        const fetchEquipments = async () => {
            try {
                const response: Equipment = await equipment.get("67be88ed9393cb4ac827e3b1");
                setEquipment_id(response);
            } catch (error) {
                console.error("Error fetching equipments:", error);
            }
        };

        fetchEquipments();
    }, []);

    useEffect(() => {
        // Subscribe to status topics using the shared MQTT connection
        subscribeTopic(`equipments/status/communication_state/${selectedEquipment}`, (msg: string) => {
            setEquipmentStatus(prev => ({ ...prev, communicationState: msg }));
        });
        subscribeTopic(`equipments/status/control_state/${selectedEquipment}`, (msg: string) => {
            setEquipmentStatus(prev => ({ ...prev, controlState: msg }));
        });
        subscribeTopic(`equipments/status/process_state/${selectedEquipment}`, (msg: string) => {
            setEquipmentStatus(prev => ({ ...prev, processState: msg }));
        });
        subscribeTopic(`equipments/status/process_program/${selectedEquipment}`, (msg: string) => {
            setEquipmentStatus(prev => ({ ...prev, processProgram: msg }));
        });

        return () => {
            // Unsubscribe from topics when equipment changes or component unmounts
            unsubscribeTopic(`equipments/status/communication_state/${selectedEquipment}`);
            unsubscribeTopic(`equipments/status/control_state/${selectedEquipment}`);
            unsubscribeTopic(`equipments/status/process_state/${selectedEquipment}`);
            unsubscribeTopic(`equipments/status/process_program/${selectedEquipment}`);
        };
    }, [selectedEquipment, subscribeTopic, unsubscribeTopic]);

    return (
        <Box sx={{ p: 2 }}>
            <Alert
                severity={connectionStatus === 'connected' ? 'success' : 'warning'}
                sx={{ mb: 3 }}
            >
                MQTT Connection Status: {connectionStatus}
            </Alert>
            <Typography variant="h6" sx={{ mb: 2 }}>Selected Equipment: {selectedEquipment}</Typography>
            <Paper elevation={3} sx={{ p: 2, mb: 3 }}>
                <Typography variant="h6">Equipment Status</Typography>
                <pre>{JSON.stringify(equipmentStatus, null, 2)}</pre>
            </Paper>

            <Divider sx={{ mb: 2 }} />
            <Typography variant="h6">Add Equipment</Typography>
            <Box component="form" sx={{ '& .MuiTextField-root': { m: 1, width: '25ch' }, border: '1px dashed grey' }} p={2}>
                <TextField id="standard-basic-name" size='small' label="Name" variant="outlined" />
                <TextField
                    id="outlined-select-model"
                    select
                    size='small'
                    label="Model"
                    defaultValue="FCL"
                >
                    {["FCL", "FCLX"].map((option) => (
                        <MenuItem key={option} value={option}>
                            {option}
                        </MenuItem>
                    ))}
                </TextField>
                <TextField size='small' id="standard-basic-ip" label="IP Address" variant="outlined" />
                <TextField size='small' id="standard-basic-port" label="Port" defaultValue={5000} variant="outlined" />
                <TextField size='small' id="standard-basic-id" label="ID" defaultValue={0} variant="outlined" />
                <TextField
                    id="outlined-select-mode"
                    select
                    size='small'
                    label="Mode"
                    defaultValue="ACTIVE"
                >
                    {["ACTIVE", "PASSIVE"].map((option) => (
                        <MenuItem key={option} value={option}>
                            {option}
                        </MenuItem>
                    ))}
                </TextField>
                <TextField
                    id="outlined-select-enable"
                    select
                    size='small'
                    label="Enable"
                    defaultValue="False"
                >
                    {["False", "True"].map((option) => (
                        <MenuItem key={option} value={option}>
                            {option}
                        </MenuItem>
                    ))}
                </TextField>
                {/* <Box sx={{ display: 'flex', mt: 2, paddingTop: 5 }}> */}
                <Button
                    // sx={{ p: 3 }}
                    sx={{ display: 'block' }}
                    variant="contained"
                    color="primary"
                    size='small'
                >
                    Add
                </Button>
                {/* </Box> */}
            </Box>
            <Divider sx={{ my: 3 }} />

            <Box component="section" sx={{ p: 2, border: '1px dashed grey' }}>
                This Box renders as an HTML section element.
            </Box>

            <Typography variant="h6">Equipment List</Typography>
            <Grid container spacing={2}>
                {equipment.list.map((equipment) => (
                    <Grid item xs={12} key={equipment._id}>
                        <Card>
                            <CardContent>
                                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                    <Typography variant="body1">{equipment.equipment_name}</Typography>
                                    <Typography variant="body2">{equipment.equipment_model}</Typography>
                                    <Typography variant="body2">{equipment.address}</Typography>
                                    <Typography variant="body2">{equipment.port}</Typography>
                                    <Typography variant="body2">{equipment.session_id}</Typography>
                                    <Typography variant="body2">{equipment.mode}</Typography>
                                    <Typography variant="body2">{equipment.enable}</Typography>
                                    <Button
                                        onClick={() => setSelectedEquipment(equipment.equipment_name)}
                                        variant="outlined"
                                        color="primary"
                                        size='small'
                                    >
                                        Select
                                    </Button>
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </Box >
    );
}
