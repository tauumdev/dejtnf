'use client';
import { useEffect, useState } from 'react';
import { publish } from '../../../../utils/mqttClient';
import { useMqtt } from '../../../../context/MqttContext';
import {
    Card,
    CardContent,
    TextField,
    Button,
    Typography,
    Alert,
    Stack,
    Grid,
    Box,
    Paper,
    Chip,
    Select,
    MenuItem,
    FormControl,
    InputLabel
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

const formatMessage = (payload: string) => {
    return payload.split('\\n').join('\n');
};

export default function Home() {
    const { connectionStatus, subscribeTopic, unsubscribeTopic } = useMqtt();

    const [topic, setTopic] = useState('equipments/control/help');
    const [message, setMessage] = useState('');
    const [primaryMessages, setPrimaryMessages] = useState<Array<{
        topic: string;
        payload: string;
        isResponse?: boolean;
        timestamp?: string;
    }>>([]);
    const [selectedEquipment, setSelectedEquipment] = useState('TNF-61'); // Default equipment
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

    const equipmentList = ['TNF-61', 'TNF-62', 'TNF-63']; // List of equipments

    useEffect(() => {
        // Reset equipment status when a new equipment is selected
        setEquipmentStatus({
            communicationState: 'Unknown',
            controlState: 'Unknown',
            processState: 'Unknown',
            processProgram: 'Unknown'
        });

        // Subscribe to status topics using the shared MQTT connection
        subscribeTopic(`equipments/status/communication_state/${selectedEquipment}`, (msg: string) => {
            console.log(`Received communication state: ${msg}`);
            setEquipmentStatus(prev => ({ ...prev, communicationState: msg }));
        });
        subscribeTopic(`equipments/status/control_state/${selectedEquipment}`, (msg: string) => {
            console.log(`Received control state: ${msg}`);
            setEquipmentStatus(prev => ({ ...prev, controlState: msg }));
        });
        subscribeTopic(`equipments/status/process_state/${selectedEquipment}`, (msg: string) => {
            console.log(`Received process state: ${msg}`);
            setEquipmentStatus(prev => ({ ...prev, processState: msg }));
        });
        subscribeTopic(`equipments/status/process_program/${selectedEquipment}`, (msg: string) => {
            console.log(`Received process program: ${msg}`);
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

    const handleSendMessage = () => {
        if (topic.trim() && message.trim()) {
            console.log('Sending message:', message, 'to topic:', topic);
            try {
                publish(topic, message);
                setPrimaryMessages(prev => {
                    const newMessages = [
                        {
                            topic: topic,
                            payload: message,
                            timestamp: new Date().toISOString()
                        },
                        ...prev
                    ];
                    return newMessages.slice(0, 30); // Keep first 30 messages
                });
                setMessage('');
            } catch (error) {
                console.error('Failed to send message:', error);
            }
        }
    };

    return (
        <Box sx={{ p: 3 }}>
            <Alert
                severity={connectionStatus === 'connected' ? 'success' : 'warning'}
                sx={{ mb: 3 }}
            >
                MQTT Connection Status: {connectionStatus}
            </Alert>

            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Stack spacing={2}>
                        <Typography variant="h6" gutterBottom>
                            Equipment Status
                        </Typography>
                        <FormControl fullWidth size="small">
                            <InputLabel>Select Equipment</InputLabel>
                            <Select
                                value={selectedEquipment}
                                onChange={(e) => setSelectedEquipment(e.target.value)}
                                label="Select Equipment"
                            >
                                {equipmentList.map((equipment) => (
                                    <MenuItem key={equipment} value={equipment}>
                                        {equipment}
                                    </MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                        <Grid container spacing={2}>
                            <Grid item xs={12} md={6}>
                                <Paper sx={{ p: 2 }}>
                                    <Typography variant="subtitle2">Communication State</Typography>
                                    <Typography variant="body1">
                                        {equipmentStatus.communicationState || 'No data available'}
                                    </Typography>
                                </Paper>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Paper sx={{ p: 2 }}>
                                    <Typography variant="subtitle2">Control State</Typography>
                                    <Typography variant="body1">
                                        {equipmentStatus.controlState || 'No data available'}
                                    </Typography>
                                </Paper>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Paper sx={{ p: 2 }}>
                                    <Typography variant="subtitle2">Process State</Typography>
                                    <Typography variant="body1">
                                        {equipmentStatus.processState || 'No data available'}
                                    </Typography>
                                </Paper>
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <Paper sx={{ p: 2 }}>
                                    <Typography variant="subtitle2">Process Program</Typography>
                                    <Typography variant="body1">
                                        {equipmentStatus.processProgram || 'No data available'}
                                    </Typography>
                                </Paper>
                            </Grid>
                        </Grid>
                    </Stack>
                </CardContent>
            </Card>

            <Card sx={{ mb: 3 }}>
                <CardContent>
                    <Stack spacing={2}>
                        <Typography variant="h6" gutterBottom>
                            MQTT Message Sender
                        </Typography>
                        <TextField
                            fullWidth
                            label="Topic"
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            size="small"
                        />
                        <Stack direction="row" spacing={2}>
                            <TextField
                                multiline
                                minRows={6}
                                maxRows={6}
                                fullWidth
                                label="Message"
                                value={message}
                                onChange={(e) => setMessage(e.target.value)}
                                size="small"
                                sx={{
                                    '& .MuiOutlinedInput-root': {
                                        minHeight: '120px',
                                        backgroundColor: 'background.paper'
                                    }
                                }}
                            />
                            <Button
                                onClick={handleSendMessage}
                                endIcon={<SendIcon />}
                                size="small"
                            >
                                Send
                            </Button>
                        </Stack>
                    </Stack>
                </CardContent>
            </Card>

            <Grid item xs={12} md={6}>
                <Card>
                    <CardContent>
                        <Typography variant="h6" gutterBottom>
                            Primary Messages (Request/Response)
                        </Typography>
                        <Stack spacing={2}>
                            {primaryMessages.map((msg, index) => (
                                <Paper
                                    key={index}
                                    elevation={0}
                                    sx={{
                                        p: 2,
                                        bgcolor: msg.isResponse ? 'success.lighter' : 'background.paper',
                                        border: '1px solid',
                                        borderColor: 'divider'
                                    }}
                                >
                                    <Stack direction="row" justifyContent="space-between" alignItems="center" mb={1}>
                                        <Typography variant="subtitle2">
                                            {msg.topic}
                                        </Typography>
                                        <Chip
                                            size="small"
                                            label={msg.isResponse ? 'Response' : 'Request'}
                                            color={msg.isResponse ? 'success' : 'default'}
                                        />
                                    </Stack>
                                    <Typography variant="caption" display="block" color="text.secondary" mb={1}>
                                        {msg.timestamp}
                                    </Typography>
                                    <Box
                                        component="pre"
                                        sx={{
                                            p: 1.5,
                                            bgcolor: 'background.paper',
                                            borderRadius: 1,
                                            fontSize: '0.875rem',
                                            fontFamily: 'monospace',
                                            whiteSpace: 'pre-wrap',
                                            overflow: 'auto',
                                            maxHeight: '300px'
                                        }}
                                    >
                                        {formatMessage(msg.payload)}
                                    </Box>
                                </Paper>
                            ))}
                        </Stack>
                    </CardContent>
                </Card>
            </Grid>
        </Box>
    );
}