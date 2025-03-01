'use client';
import React, { useEffect, useState } from 'react'
import { useMqtt } from '../../../../context/MqttContext';
import { Alert, Box, Button, TextField, Typography } from '@mui/material';

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

                const response: Equipment = await equipment.get("67c2e4308c20b6f12ae73854");
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
            // console.log(`Received communication state: ${msg}`);
            setEquipmentStatus(prev => ({ ...prev, communicationState: msg }));
        });
        subscribeTopic(`equipments/status/control_state/${selectedEquipment}`, (msg: string) => {
            // console.log(`Received control state: ${msg}`);
            setEquipmentStatus(prev => ({ ...prev, controlState: msg }));
        });
        subscribeTopic(`equipments/status/process_state/${selectedEquipment}`, (msg: string) => {
            // console.log(`Received process state: ${msg}`);
            setEquipmentStatus(prev => ({ ...prev, processState: msg }));
        });
        subscribeTopic(`equipments/status/process_program/${selectedEquipment}`, (msg: string) => {
            // console.log(`Received process program: ${msg}`);
            setEquipmentStatus(prev => ({ ...prev, processProgram: msg }));
        });

        return () => {
            // Unsubscribe from topics when equipment changes or component unmounts
            unsubscribeTopic(`equipments/status/communication_state/${selectedEquipment}`);
            unsubscribeTopic(`equipments/status/control_state/${selectedEquipment}`);
            unsubscribeTopic(`equipments/status/process_state/${selectedEquipment}`);
            unsubscribeTopic(`equipments/status/process_program/${selectedEquipment}`);
        };

    }, [selectedEquipment, subscribeTopic, unsubscribeTopic])


    // {
    //     "mode": "ACTIVE",
    //     "_id": "67c2e4308c20b6f12ae73854",
    //     "equipment_name": "TNF-64",
    //     "equipment_model": "FCL",
    //     "address": "192.168.226.164",
    //     "port": 5000,
    //     "session_id": 64,
    //     "enable": false,
    //     "createdAt": "2025-03-01T10:40:48.020Z",
    //     "updatedAt": "2025-03-01T10:40:48.020Z"
    //   }

    return (
        <Box sx={{ p: 2 }}>
            <Alert
                severity={connectionStatus === 'connected' ? 'success' : 'warning'}
                sx={{ mb: 3 }}
            >
                MQTT Connection Status: {connectionStatus}
            </Alert>
            <Typography>{selectedEquipment}</Typography>
            {/* <Typography>Equipment by id: 67c2e4308c20b6f12ae73854</Typography> */}
            <pre>{JSON.stringify(equipmentStatus, null, 2)}</pre>
            <Typography>Add Equipment</Typography>


            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <TextField id="standard-basic" label="Equipment name" variant="standard" />

                <Button
                    // onClick={() => setSelectedEquipment(equipment_id?.equipment_name || '')}
                    variant="outlined"
                    color="primary"
                    size='small'
                >
                    Add
                </Button>
            </Box>

            {/* {equipment.loading && <Typography>Loading...</Typography>}
 */}

            <Typography>Equipment list</Typography>
            {equipment.list.map((equipment) => (
                <Box key={equipment._id}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <li>{equipment.equipment_name}</li>
                        <Typography>{equipment.equipment_model}</Typography>
                        <Typography>{equipment.address}</Typography>
                        <Typography>{equipment.port}</Typography>
                        <Typography>{equipment.session_id}</Typography>
                        <Typography>{equipment.mode}</Typography>
                        <Typography>{equipment.enable}</Typography>
                        <Button
                            onClick={() => setSelectedEquipment(equipment.equipment_name)}
                            variant="outlined"
                            color="primary"
                            size='small'
                        >
                            Select
                        </Button>
                    </Box>
                </Box>
            ))}

        </Box >
    )
}
