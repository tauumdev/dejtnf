'use client';
import { log } from 'console';
import { useMqtt } from '../../../../context/MqttContext';
import React, { useEffect, useState } from 'react';
import { Card, CardContent, Chip, keyframes, Stack, Typography } from '@mui/material';
import { stat } from 'fs';

type AlarmState = {
    alid: string;
    altext: string;
};

type EquipmentStatus = {
    communicationState: string;
    processProgram: string;
    controlState: string;
    processState: string;
    activeLot: string;
    alarmState: AlarmState[];
};

export default function Page() {
    const { subscribeTopic, unsubscribeTopic, connectionStatus } = useMqtt();
    const [status, setStatus] = useState<EquipmentStatus>({
        communicationState: '',
        processProgram: '',
        controlState: '',
        processState: '',
        activeLot: '',
        alarmState: [] // initial empty array.
    });

    useEffect(() => {
        const equipmentName = 'TNF-61';
        const topics = [
            { key: 'communicationState', topic: `equipments/status/communication_state/${equipmentName}` },
            { key: 'processProgram', topic: `equipments/status/process_program/${equipmentName}` },
            { key: 'controlState', topic: `equipments/status/control_state/${equipmentName}` },
            { key: 'processState', topic: `equipments/status/process_state/${equipmentName}` },
            { key: 'activeLot', topic: `equipments/status/active_lot/${equipmentName}` },
            { key: 'alarmState', topic: `equipments/status/alarm_state/${equipmentName}/#` }
        ];

        const subscriptions = topics.map((item) => {
            const callback = (msg: string, topic: string) => {
                console.log("<!!!> msg: ", msg, "topic: ", topic);
                if (item.key === 'alarmState') {
                    // Extract alarm id from topic
                    const prefix = `equipments/status/alarm_state/${equipmentName}/`;
                    if (topic.startsWith(prefix)) {
                        const alid = topic.split('/').pop() || '';
                        const altext = msg.trim();
                        if (altext === '') {
                            setStatus((prev) => ({
                                ...prev,
                                alarmState: prev.alarmState.filter((alarm) => alarm.alid !== alid)
                            }));
                        } else {
                            setStatus((prev) => {
                                // Only add alarm if not already present
                                if (!prev.alarmState.some((alarm) => alarm.alid === alid)) {
                                    return { ...prev, alarmState: [...prev.alarmState, { alid, altext }] };
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
            }
            subscribeTopic(item.topic, callback);
            return { topic: item.topic, callback };
        });

        return () => {
            subscriptions.forEach(({ topic, callback }) => {
                unsubscribeTopic(topic, callback);
            });
        };

    }, [subscribeTopic, unsubscribeTopic]);

    const processStateColor: { [key: string]: 'default' | 'primary' | 'secondary' | 'red' | 'info' | 'success' | 'warning' | 'blue' | 'text.secondary' } = {
        'Idle': 'warning', //fclx
        'Starting': 'success',
        'Running': 'success',
        'Stopping': 'success',
        'Pausing': 'warning',
        'Alarm Paused': 'red',
        'Engineering': 'red',
        'Unknown': 'default',

        'No State': 'default', //fcl
        'Initialize': 'blue',
        'Not Standby': 'default',
        'Standby': 'warning',
        'Running Executing': 'success',
        'Running Pause': 'success',
        'Running Empty': 'success',
        'Specific Running': 'success',
        'Error Waiting': 'red',
        'Error Assisting': 'red',
        '': "text.secondary"
    };

    // Define a blinking animation for the alarm indicator
    const blink = keyframes`
      0% { opacity: 1; }
      50% { opacity: 0; }
      100% { opacity: 1; }
    `;

    return (
        <Card variant="outlined" sx={{ height: '100%', flexGrow: 1 }}>
            <CardContent>

                <Stack direction="column" sx={{ justifyContent: 'space-between', flexGrow: '1', gap: 1 }}>
                    <Stack sx={{ justifyContent: 'space-between' }}>
                        <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center' }}>

                            <Typography variant='subtitle1' component="p" color={
                                status.communicationState === "COMMUNICATING" ? 'default' : 'text.secondary'
                            }> TNF-61</Typography>

                            <Typography
                                variant='subtitle2'
                                color={processStateColor[status.processState as keyof typeof processStateColor]}
                                sx={
                                    status.processState === 'Error Waiting' || status.processState === 'Error Assisting' || status.processState === 'Alarm Paused'
                                        ? { animation: `${blink} 1.3s infinite` }
                                        : undefined
                                }
                            >
                                {status.processState !== '' ? status.processState : 'Disconnected'}
                            </Typography>

                        </Stack>
                        <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                            {status.controlState}
                        </Typography>
                        <Stack direction="row" sx={{ justifyContent: 'space-between', alignItems: 'center' }}>
                            <Typography variant="subtitle2" component="p">
                                {status.processProgram}
                            </Typography>
                            <Typography variant="subtitle2" component="p">
                                {status.activeLot}
                            </Typography>
                        </Stack>

                    </Stack>
                </Stack>

            </CardContent>
        </Card >
    );
}
