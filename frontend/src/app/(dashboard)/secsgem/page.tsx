'use client';
import { useEffect, useState } from 'react';
import { connectMqtt, subscribe, publish } from '../../../utils/mqttClient';

export default function Home() {
  const [topic, setTopic] = useState('equipments/status');
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Array<{ topic: string, payload: string }>>([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  useEffect(() => {
    const client = connectMqtt(
      () => {
        setConnectionStatus('connected');
        subscribe('equipments/status/#', (msg, receivedTopic) => {
          setMessages(prev => {
            const newMessages = [...prev, { topic: receivedTopic, payload: msg }];
            return newMessages.slice(-30); // Keep only last 30 messages
          });
        });
      },
      () => setConnectionStatus('error'),
      (message, receivedTopic) => {
        setMessages(prev => {
          const newMessages = [...prev, { topic: receivedTopic, payload: message }];
          return newMessages.slice(-30); // Keep only last 30 messages
        });
      }
    );

    return () => {
      if (client && client.isConnected()) {
        client.disconnect();
      }
    };
  }, []);

  const handleSendMessage = () => {
    if (topic.trim() && message.trim()) {
      try {
        publish(topic, message);
        // Update UI immediately for better UX
        setMessages(prev => {
          const newMessages = [{ topic, payload: message }, ...prev];
          return newMessages.slice(0, 30); // Keep most recent 30 messages
        });
        setMessage(''); // Clear message input
      } catch (error) {
        console.error('Failed to send message:', error);
        setConnectionStatus('error');
      }
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <div style={{
        padding: '10px',
        marginBottom: '20px',
        backgroundColor: connectionStatus === 'connected' ? '#d4edda' : '#f8d7da',
        borderRadius: '4px'
      }}>
        Status: {connectionStatus}
      </div>

      <div style={{ marginBottom: '20px' }}>
        <div style={{ marginBottom: '10px' }}>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Topic"
            style={{
              padding: '8px',
              marginRight: '10px',
              borderRadius: '4px',
              border: '1px solid #ddd',
              width: '200px'
            }}
          />
        </div>
        <div>
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Message"
            style={{
              padding: '8px',
              marginRight: '10px',
              borderRadius: '4px',
              border: '1px solid #ddd',
              width: '200px'
            }}
          />
          <button
            onClick={handleSendMessage}
            style={{
              padding: '8px 16px',
              borderRadius: '4px',
              border: 'none',
              backgroundColor: '#007bff',
              color: 'white',
              cursor: 'pointer'
            }}
          >
            Send
          </button>
        </div>
      </div>

      <h2>MQTT Messages:</h2>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {[...messages].reverse().map((msg, index) => (
          <li key={index} style={{
            marginBottom: '10px',
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}>
            <strong>Topic:</strong> {msg.topic}<br />
            <strong>Message:</strong> {msg.payload}
          </li>
        ))}
      </ul>
    </div>
  );
}