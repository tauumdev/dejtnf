import axios from 'axios';

const API_URL_VALIDATE_CONFIG = 'http://localhost:3000/api/validate';

export const getConfigs = async () => {
    const response = await axios.get(`${API_URL_VALIDATE_CONFIG}/configs`);
    console.log(response);
    return response.data;
};

export const getConfigById = async (id) => {
    const response = await axios.get(`${API_URL_VALIDATE_CONFIG}/config/${id}`);
    console.log(response);
    return response.data;
};

export const createConfig = async (config) => {
    const response = await axios.post(`${API_URL_VALIDATE_CONFIG}/config`, config);
    console.log(response);
    return response.data;
};

export const updateConfig = async (id, config) => {
    const response = await axios.put(`${API_URL_VALIDATE_CONFIG}/config/${id}`, config);
    console.log(response);
    return response.data;
};

export const deleteConfig = async (id) => {
    const response = await axios.delete(`${API_URL_VALIDATE_CONFIG}/config/${id}`);
    console.log(response);
    return response.data;
};



สร้าง context dejtnfapi จากข้างบน ให้เหมือนเหมือนข้างล่างได้ไหม ข้างล่างคือรูปแบบตัวอย่าง

'use client';
import React, { createContext, useContext, useEffect, useRef, useState, ReactNode, useCallback } from 'react';
import { connectMqtt, disconnectMqtt, subscribe, unsubscribe } from '../../src/utils/mqttClient';

interface MqttContextType {
    connectionStatus: string;
    subscribeTopic: (topic: string, callback: (msg: string, topic: string) => void) => void;
    unsubscribeTopic: (topic: string, callback?: (msg: string, topic: string) => void) => void;
}

const MqttContext = createContext < MqttContextType | undefined > (undefined);

export function MqttProvider({ children }: { children: ReactNode }) {
    const [connectionStatus, setConnectionStatus] = useState('disconnected');
    const clientRef = useRef < any > (null);
    // Maintain a mapping of topic -> array of callbacks
    const subscriptionsRef = useRef < { [key: string]: Array<(msg: string, topic: string) => void> }> ({});

// Global onMessage will dispatch to all callbacks for that topic
const globalOnMessage = useCallback((message: string, receivedTopic: string) => {
    console.log(`Global MQTT message: ${message} on topic: ${receivedTopic}`);

    // Iterate over all subscribed topics
    Object.entries(subscriptionsRef.current).forEach(([topic, callbacks]) => {
        // Check if the received topic matches the subscribed topic (including wildcards)
        if (topicMatchesWildcard(receivedTopic, topic)) {
            callbacks.forEach((cb) => cb(message, receivedTopic));
        }
    });
}, []);

// Helper function to check if a topic matches a wildcard pattern
const topicMatchesWildcard = (receivedTopic: string, subscribedTopic: string) => {
    if (subscribedTopic.endsWith('/#')) {
        // Wildcard match: check if the received topic starts with the prefix
        const prefix = subscribedTopic.slice(0, -2); // Remove '/#' from the end
        return receivedTopic.startsWith(prefix);
    } else {
        // Exact match
        return receivedTopic === subscribedTopic;
    }
};

const onConnect = useCallback(() => {
    setConnectionStatus('connected');
    console.log('MQTT connected');
}, []);

const onError = useCallback((error: any) => {
    console.error('MQTT connection error:', error);
    setConnectionStatus('error');
}, []);

useEffect(() => {
    if (!clientRef.current || !clientRef.current.isConnected?.()) {
        clientRef.current = connectMqtt(onConnect, onError, globalOnMessage);
    }

    return () => {
        // Disconnect only once when provider unmounts
        if (clientRef.current && clientRef.current.isConnected?.()) {
            disconnectMqtt(clientRef.current);
        }
    };
}, [onConnect, onError, globalOnMessage]);

const subscribeTopic = (topic: string, callback: (msg: string, topic: string) => void) => {
    // Store the callback in our subscriptions mapping
    if (!subscriptionsRef.current[topic]) {
        subscriptionsRef.current[topic] = [];
        // Do the actual subscription on the client only once per topic
        if (clientRef.current && clientRef.current.isConnected?.()) {
            subscribe(topic, globalOnMessage);
        }
    }
    subscriptionsRef.current[topic].push(callback);
    console.log(`Subscribed to ${topic} (callbacks count: ${subscriptionsRef.current[topic].length})`);
};

const unsubscribeTopic = (topic: string, callback?: (msg: string, topic: string) => void) => {
    if (!subscriptionsRef.current[topic]) return;
    if (callback) {
        subscriptionsRef.current[topic] = subscriptionsRef.current[topic].filter(
            (cb) => cb !== callback
        );
    } else {
        // Remove all callbacks for that topic if no callback is provided
        delete subscriptionsRef.current[topic];
    }
    // If no callbacks remain, unsubscribe at the MQTT client level.
    if (!subscriptionsRef.current[topic] || subscriptionsRef.current[topic].length === 0) {
        if (clientRef.current && clientRef.current.isConnected?.()) {
            unsubscribe(topic);
        }
        delete subscriptionsRef.current[topic];
        console.log(`Unsubscribed from ${topic}`);
    }
};

return (
    <MqttContext.Provider value={{ connectionStatus, subscribeTopic, unsubscribeTopic }}>
        {children}
    </MqttContext.Provider>
);
}

export function useMqtt() {
    const context = useContext(MqttContext);
    if (!context) {
        throw new Error('useMqtt must be used within a MqttProvider');
    }
    return context;
}