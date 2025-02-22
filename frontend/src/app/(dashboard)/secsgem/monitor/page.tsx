'use client';
import { useEffect, useState } from 'react';
import { useMqtt } from '../../../../context/MqttContext';
import {
    Box,
    Card,
    CardContent,
    Typography,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Stack,
    Grid,
    Alert,
    Chip,
    Divider
} from '@mui/material';
import { keyframes } from '@mui/material/styles';

type EquipmentStatus = {
    communicationState: string;
    processProgram: string;
    controlState: string;
    processState: string;
    alarmState: string[]; // Array of alarms
};

// Define a blinking animation for the alarm indicator
const blink = keyframes`
  0% { opacity: 1; }
  50% { opacity: 0; }
  100% { opacity: 1; }
`;

function EquipmentStatusCard({ equipmentName }: { equipmentName: string }) {
    const { subscribeTopic, unsubscribeTopic } = useMqtt();
    const [status, setStatus] = useState<EquipmentStatus>({
        communicationState: 'Unknown',
        processProgram: 'Unknown',
        controlState: 'Unknown',
        processState: 'Unknown',
        alarmState: [] // initial empty array.
    });

    useEffect(() => {
        const topics = [
            { key: 'communicationState', topic: `equipments/status/communication_state/${equipmentName}` },
            { key: 'processProgram', topic: `equipments/status/process_program/${equipmentName}` },
            { key: 'controlState', topic: `equipments/status/control_state/${equipmentName}` },
            { key: 'processState', topic: `equipments/status/process_state/${equipmentName}` },
            { key: 'alarmState', topic: `equipments/status/alarm_state/${equipmentName}/#` }
        ];

        const subscriptions = topics.map((item) => {
            const callback = (msg: string, topic: string) => {
                if (item.key === 'alarmState') {
                    const prefix = `equipments/status/alarm_state/${equipmentName}/`;
                    if (topic.startsWith(prefix)) {
                        const trimmedMsg = msg.trim();
                        if (trimmedMsg) {
                            console.log(`Alarm received for ${equipmentName}: ${trimmedMsg}`);
                            // Append the alarm message if not already present
                            setStatus((prev) => {
                                if (!prev.alarmState.includes(trimmedMsg)) {
                                    return { ...prev, alarmState: [...prev.alarmState, trimmedMsg] };
                                }
                                return prev;
                            });
                        }
                    }
                } else {
                    setStatus((prev) => ({
                        ...prev,
                        [item.key]: msg
                    }));
                }
            };
            subscribeTopic(item.topic, callback);
            return { topic: item.topic, callback };
        });

        return () => {
            subscriptions.forEach(({ topic, callback }) => {
                unsubscribeTopic(topic, callback);
            });
        };
    }, [equipmentName, subscribeTopic, unsubscribeTopic]);

    return (
        <Card sx={{ mb: 3, boxShadow: 3, position: 'relative' }}>
            <CardContent>
                {/* Header with equipment name and alarm indicator */}
                <Box sx={{ position: 'relative', mb: 2 }}>
                    <Typography variant="h6" color="primary" sx={{ fontWeight: 'bold' }}>
                        {equipmentName}
                    </Typography>
                    {status.alarmState.length > 0 && (
                        <Box
                            sx={{
                                position: 'absolute',
                                top: 0,
                                right: 0,
                                width: 12,
                                height: 12,
                                borderRadius: '50%',
                                backgroundColor: 'error.main',
                                animation: `${blink} 1s infinite`
                            }}
                        />
                    )}
                </Box>
                <Divider sx={{ mb: 2 }} />
                <Stack spacing={1}>
                    <Typography variant="body1">
                        <strong>Communication:</strong> {status.communicationState}
                    </Typography>
                    <Typography variant="body1">
                        <strong>Process Program:</strong> {status.processProgram}
                    </Typography>
                    <Typography variant="body1">
                        <strong>Control:</strong> {status.controlState}
                    </Typography>
                    <Typography variant="body1">
                        <strong>Process:</strong> {status.processState}
                    </Typography>
                    <Box>
                        <Typography variant="body1" sx={{ mb: 1 }}>
                            <strong>Alarms:</strong>
                        </Typography>
                        {status.alarmState.length > 0 ? (
                            <Stack direction="row" spacing={1} flexWrap="wrap">
                                {status.alarmState.map((alarm, index) => (
                                    <Chip key={index} label={alarm} variant="outlined" color="error" sx={{ mb: 1 }} />
                                ))}
                            </Stack>
                        ) : (
                            <Typography variant="body2" color="text.secondary">
                                No Alarm
                            </Typography>
                        )}
                    </Box>
                </Stack>
            </CardContent>
        </Card>
    );
}

export default function Page() {
    const { connectionStatus } = useMqtt();
    const equipmentList = ['TNF-61', 'TNF-62', 'TNF-63'];
    const [selectedEquipment, setSelectedEquipment] = useState(equipmentList[0]);

    return (
        <Box sx={{ p: 3 }}>
            <Typography variant="h4" gutterBottom>
                Monitor Equipment Status
            </Typography>
            <Typography variant="body1" gutterBottom color="text.secondary">
                This is the Monitor equipment status page.
            </Typography>

            <Stack spacing={2} sx={{ my: 3 }}>
                <Alert severity={connectionStatus === 'connected' ? 'success' : 'warning'}>
                    MQTT Connection Status: {connectionStatus}
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

            <Grid container spacing={3}>
                {equipmentList.map((equipment) => (
                    <Grid key={equipment} item xs={12} md={6}>
                        <EquipmentStatusCard equipmentName={equipment} />
                    </Grid>
                ))}
            </Grid>
        </Box>
    );
}
