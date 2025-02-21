"use client";
// import React, { useEffect, useState } from 'react';
import { connectMqtt, subscribe, publish } from '../../../../utils/mqttClient';

import { useEffect, useState } from 'react';
// import { connectMqtt, subscribe } from '../path/to/your/mqtt-client'; // Adjust the import path

const MqttMonitor = () => {
    const [messages, setMessages] = useState([]);

    useEffect(() => {
        const onConnect = () => {
            console.log('Connected to MQTT broker');
            subscribe('equipments/status/secs_message/TNF-61', (message, topic) => {
                setMessages(prevMessages => [...prevMessages, { topic, message }]);
            });
        };

        const onError = (error) => {
            console.error('MQTT connection error:', error);
        };

        const onMessage = (message, topic) => {
            setMessages(prevMessages => [...prevMessages, { topic, message }]);
        };

        const client = connectMqtt(onConnect, onError, onMessage);

        return () => {
            if (client && client.isConnected()) {
                client.disconnect();
            }
        };
    }, []);

    return (
        <div>
            <h1>MQTT Monitor</h1>
            <ul>
                {messages.map((msg, index) => (
                    <li key={index}>
                        <strong>Topic:</strong> {msg.topic} <br />
                        <strong>Message:</strong> {msg.message}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default MqttMonitor;