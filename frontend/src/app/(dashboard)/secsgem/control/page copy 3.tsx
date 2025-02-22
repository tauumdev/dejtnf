'use client';
import { useEffect, useState, useCallback } from 'react';
import { useMqtt } from '../../../../context/MqttContext';
import {
    Box,
    Card,
    CardContent,
    Typography,
    Alert,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Stack
} from '@mui/material';

export default function Page() {
    const { connectionStatus, subscribeTopic, unsubscribeTopic } = useMqtt();
    const [selectedEquipment, setSelectedEquipment] = useState('TNF-61');
    const [messages, setMessages] = useState<string>('');
    const equipmentList = ['TNF-61', 'TNF-62', 'TNF-63'];
    const topic = `equipments/status/communication_state/${selectedEquipment}`;

    // Local callback to handle messages
    const onMessage = useCallback((message: string, receivedTopic: string) => {
        console.log(`Received message on page: ${message} from ${receivedTopic}`);
        setMessages(message);
    }, []);

    useEffect(() => {
        console.log('Page mounted or equipment changed');
        subscribeTopic(topic, onMessage);

        return () => {
            console.log('Page cleanup: unsubscribing from', topic);
            unsubscribeTopic(topic, onMessage);
            setMessages('');
        };
    }, [selectedEquipment, topic, onMessage, subscribeTopic, unsubscribeTopic]);

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>
                Control
            </Typography>
            <Typography variant="body1" gutterBottom>
                This is the Control page.
            </Typography>

            <Stack spacing={2} sx={{ my: 3 }}>
                <Alert severity={connectionStatus === 'connected' ? 'success' : 'warning'}>
                    Mqtt Connection Status: {connectionStatus}
                </Alert>

                <FormControl fullWidth sx={{ maxWidth: 300 }}>
                    <InputLabel id="equipment-select-label">Select Equipment</InputLabel>
                    <Select
                        labelId="equipment-select-label"
                        id="equipment-select"
                        value={selectedEquipment}
                        label="Select Equipment"
                        onChange={(e) => setSelectedEquipment(e.target.value)}
                    >
                        {equipmentList.map((equipment) => (
                            <MenuItem key={equipment} value={equipment}>
                                {equipment}
                            </MenuItem>
                        ))}
                    </Select>
                </FormControl>
            </Stack>

            <Card>
                <CardContent>
                    <Typography variant="h6" gutterBottom>
                        Received Messages
                    </Typography>
                    <Typography variant="body1">
                        {messages || 'No messages received.'}
                    </Typography>
                </CardContent>
            </Card>
        </Box>
    );
}