// import { Client, Message as PahoMessage } from 'paho-mqtt';
import { Client } from 'paho-mqtt';
const MQTT_CONFIG = {
    host: process.env.NEXT_PUBLIC_MQTT_HOST || 'localhost',
    port: parseInt(process.env.NEXT_PUBLIC_MQTT_PORT) || 8081, // Changed to typical MQTT-WS port
    username: process.env.NEXT_PUBLIC_MQTT_USER,
    password: process.env.NEXT_PUBLIC_MQTT_PASS,
    clientId: `paho-client-${Math.random().toString(16).slice(2)}`,
    reconnectTimeout: 5000
};

let client = null;
let reconnectTimer = null;

const connect = (onConnect, onError) => {
    const connectOptions = {
        useSSL: false,
        userName: MQTT_CONFIG.username,
        password: MQTT_CONFIG.password,
        onSuccess: () => {
            console.log('Connected to MQTT broker');
            if (onConnect) onConnect();
        },
        onFailure: (error) => {
            console.error('Connection failed:', error.errorMessage);
            if (onError) onError(error);
            // Retry connection
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
        if (onError) onError(error);
    }
};

export const connectMqtt = (onConnect, onError, onMessage) => {
    if (!client) {
        // Create WebSocket URL with correct format
        client = new Client(
            MQTT_CONFIG.host,
            Number(MQTT_CONFIG.port),
            '', // Empty path, let broker handle WebSocket upgrade
            MQTT_CONFIG.clientId
        );

        client.onConnectionLost = (responseObject) => {
            if (responseObject.errorCode !== 0) {
                console.warn('Connection lost:', responseObject.errorMessage);
                if (onError) onError(responseObject);
                // Retry connection
                reconnectTimer = setTimeout(() => {
                    console.log('Reconnecting...');
                    connect(onConnect, onError);
                }, MQTT_CONFIG.reconnectTimeout);
            }
        };

        client.onMessageArrived = (message) => {
            if (onMessage) onMessage(message.payloadString, message.destinationName);
        };

        connect(onConnect, onError);
    }
    return client;
};

export const subscribe = (topic, callback) => {
    if (client && client.isConnected()) {
        client.subscribe(topic, {
            qos: 0,
            onSuccess: () => {
                console.log(`Subscribed to ${topic}`);
                // Send test message to confirm subscription

                // let hello_topic = "website/Connection";
                // let hello_payload = "hello from website";
                // client.publish(hello_topic, hello_payload);

            },
            onFailure: (error) => {
                console.error(`Subscribe failed: ${error.errorMessage}`);
            }
        });
    } else {
        console.warn('MQTT client not connected');
    }
};

export const publish = (topic, payload) => {
    if (client && client.isConnected()) {
        try {
            client.send(topic, payload, 0, false);
            console.log('Message sent:', { topic, payload });
        } catch (error) {
            console.error('Failed to send message:', error);
            throw error;
        }
    } else {
        throw new Error('MQTT client not connected');
    }
};

export const unsubscribe = (topic) => {
    if (client && client.isConnected()) {
        client.unsubscribe(topic, {
            onSuccess: () => {
                console.log(`Unsubscribed from ${topic}`);
            },
            onFailure: (error) => {
                console.error(`Unsubscribe failed: ${error.errorMessage}`);
            }
        });
    } else {
        console.warn('MQTT client not connected');
    }
};
export default client;
