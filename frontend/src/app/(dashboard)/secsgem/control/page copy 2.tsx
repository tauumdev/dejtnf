'use client';
import { useEffect, useState, useCallback, useRef } from 'react';
import { connectMqtt, disconnectMqtt, subscribe, unsubscribe } from '../../../../utils/mqttClient';
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
    const [connectionStatus, setConnectionStatus] = useState('disconnected');
    const [selectedEquipment, setSelectedEquipment] = useState('TNF-61');
    const [messages, setMessages] = useState<string>(''); // Store received messages
    const equipmentList = ['TNF-61', 'TNF-62', 'TNF-63'];
    const topic = `equipments/status/communication_state/${selectedEquipment}`;

    // Persist the client connection across mounts
    const clientRef = useRef<any>(null);

    // Memoize onMessage to prevent unnecessary re-creation
    const onMessage = useCallback((message: string, receivedTopic: string) => {
        console.log(`Received message: ${message} on topic: ${receivedTopic}`);
        setMessages(message);
    }, []);

    // Memoize onConnect
    const onConnect = useCallback(() => {
        setConnectionStatus('connected');
        console.log(`Subscribing to topic: ${topic}`);
        subscribe(topic, onMessage);
    }, [topic, onMessage]);

    // Memoize onError
    const onError = useCallback((error: any) => {
        console.error('Connection error:', error);
        setConnectionStatus('error');
    }, []);

    useEffect(() => {
        console.log('Component mounted or equipment changed');
        // If no client exists or it’s not connected yet, create one
        if (!clientRef.current || !clientRef.current.isConnected?.()) {
            clientRef.current = connectMqtt(onConnect, onError, onMessage);
        } else {
            // The client exists; update the subscription for the new topic.
            subscribe(topic, onMessage);
        }

        return () => {
            console.log('Cleanup: Unsubscribing from topic:', topic);
            // Only unsubscribe from the topic,
            // but do not disconnect the client so that connection persists
            unsubscribe(topic);
            setMessages('');
            // Optionally, if you want to force disconnect on full refresh,
            // you may call disconnectMqtt(clientRef.current) here.
            // But to persist connection between page changes, leave it out.
            setConnectionStatus(clientRef.current?.isConnected?.() ? 'connected' : 'disconnected');
        };
    }, [selectedEquipment, topic, onConnect, onError, onMessage]);

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
                    Connection Status: {connectionStatus}
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