import { Client, Message as PahoMessage } from 'paho-mqtt';

const MQTT_CONFIG = {
    host: process.env.NEXT_PUBLIC_MQTT_HOST || 'localhost',
    port: parseInt(process.env.NEXT_PUBLIC_MQTT_PORT || '8081'), // Default WebSocket MQTT port
    username: process.env.NEXT_PUBLIC_MQTT_USER || '',
    password: process.env.NEXT_PUBLIC_MQTT_PASS || '',
    clientId: `paho-client-${Math.random().toString(16).slice(2)}`,
    reconnectTimeout: 5000
};

let client: Client | null = null;
let reconnectTimer: NodeJS.Timeout | null = null;

type MQTTCallback = (message: string, topic: string) => void;

type MQTTError = { errorMessage: string };

type ConnectionLostResponse = { errorCode: number; errorMessage: string };

const connect = (onConnect?: () => void, onError?: (error: MQTTError) => void): void => {
    if (!client) return;

    const connectOptions = {
        useSSL: false,
        userName: MQTT_CONFIG.username,
        password: MQTT_CONFIG.password,
        onSuccess: () => {
            console.log('Connected to MQTT broker');
            onConnect?.();
        },
        onFailure: (error: MQTTError) => {
            console.error('Connection failed:', error.errorMessage);
            onError?.(error);

            reconnectTimer = setTimeout(() => {
                console.log('Retrying connection...');
                connect(onConnect, onError);
            }, MQTT_CONFIG.reconnectTimeout);
        }
    };

    try {
        client.connect(connectOptions);
    } catch (error) {
        console.error('Connection error:', error);
        onError?.(error as MQTTError);
    }
};

export const disconnectMqtt = (): void => {
    if (client?.isConnected()) {
        try {
            client.disconnect();
            console.log('Disconnected from MQTT broker');
        } catch (error) {
            console.error('Error while disconnecting:', error);
        } finally {
            client = null;
            if (reconnectTimer) clearTimeout(reconnectTimer);
        }
    } else {
        console.warn('MQTT client is not connected or already disconnected');
    }
};

export const connectMqtt = (
    onConnect?: () => void,
    onError?: (error: MQTTError) => void,
    onMessage?: MQTTCallback
): Client => {
    if (!client) {
        client = new Client(
            MQTT_CONFIG.host,
            Number(MQTT_CONFIG.port),
            '',
            MQTT_CONFIG.clientId
        );

        client.onConnectionLost = (responseObject: ConnectionLostResponse) => {
            if (responseObject.errorCode !== 0) {
                console.warn('Connection lost:', responseObject.errorMessage);
                onError?.(responseObject);

                reconnectTimer = setTimeout(() => {
                    console.log('Reconnecting...');
                    connect(onConnect, onError);
                }, MQTT_CONFIG.reconnectTimeout);
            }
        };

        client.onMessageArrived = (message: PahoMessage) => {
            console.log(`Message received on topic: ${message.destinationName}, payload: ${message.payloadString}`);
            onMessage?.(message.payloadString, message.destinationName);
        };

        connect(onConnect, onError);
    }
    return client;
};

export const subscribe = (topic: string, callback?: () => void): void => {
    if (client?.isConnected()) {
        client.subscribe(topic, {
            qos: 0,
            onSuccess: () => {
                console.log(`Subscribed to ${topic}`);
                callback?.();
            },
            onFailure: (error: MQTTError) => {
                console.error(`Subscribe failed: ${error.errorMessage}`);
            }
        });
    } else {
        console.warn('MQTT client not connected');
    }
};

export const publish = (topic: string, payload: string): void => {
    if (client?.isConnected()) {
        try {
            const message = new PahoMessage(payload);
            message.destinationName = topic;
            client.send(message);
            console.log('Message sent:', { topic, payload });
        } catch (error) {
            console.error('Failed to send message:', error);
            throw error;
        }
    } else {
        throw new Error('MQTT client not connected');
    }
};

export const unsubscribe = (topic: string): void => {
    if (client?.isConnected()) {
        client.unsubscribe(topic, {
            onSuccess: () => {
                console.log(`Unsubscribed from ${topic}`);
            },
            onFailure: (error: MQTTError) => {
                console.error(`Unsubscribe failed: ${error.errorMessage}`);
            }
        });
    } else {
        console.warn('MQTT client not connected');
    }
};

export default client;
