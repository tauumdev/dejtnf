'use client';
import { useEffect, useState } from 'react';
import { connectMqtt, subscribe, unsubscribe, publish } from '../../../utils/mqttClient';
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
  Chip
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

const formatMessage = (payload: string) => {
  return payload.split('\\n').join('\n');
};

export default function Home() {
  const [topic, setTopic] = useState('equipments/control/help');
  const [message, setMessage] = useState('');
  const [primaryMessages, setPrimaryMessages] = useState<Array<{
    topic: string,
    payload: string,
    isResponse?: boolean,
    timestamp?: string
  }>>([]);
  const [secondaryMessages, setSecondaryMessages] = useState<Array<{
    topic: string,
    payload: string
  }>>([]);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');

  useEffect(() => {
    interface Message {
      topic: string;
      payload: string;
      isResponse?: boolean;
      timestamp?: string;
    }

    interface MqttClient {
      isConnected: () => boolean;
      disconnect: () => void;
    }

    const client: MqttClient = connectMqtt(
      () => {
        setConnectionStatus('connected');
        subscribe('equipments/status/#', (msg: string, receivedTopic: string) => {
          // Handle as secondary message
          setSecondaryMessages((prev: Message[]) => {
            const newMessages = [
              { topic: receivedTopic, payload: msg },
              ...prev
            ];
            return newMessages.slice(0, 30); // Keep first 30 messages
          });
        });
      },
      () => setConnectionStatus('error'),
      (message: string, receivedTopic: string) => {
        // Check if this is a response message
        if (receivedTopic.includes('/response')) {
          setPrimaryMessages((prev: Message[]) => {
            const newMessages = [
              {
                topic: receivedTopic,
                payload: message,
                isResponse: true,
                timestamp: new Date().toISOString()
              },
              ...prev
            ];
            unsubscribe(receivedTopic); // Unsubscribe after receiving response
            return newMessages.slice(0, 30); // Keep first 30 messages
          });
        } else {
          setSecondaryMessages((prev: Message[]) => {
            const newMessages = [
              { topic: receivedTopic, payload: message },
              ...prev
            ];
            return newMessages.slice(0, 30); // Keep first 30 messages
          });
        }
      }
    );

    return () => {
      if (client && client.isConnected()) {
        client.disconnect();
      }
    };
  }, []);

  const getResponseTopic = (originalTopic: string) => {
    const parts = originalTopic.split('/');
    if (parts[0] === 'equipments') {
      return `equipments/response/${parts.slice(1).join('/')}`;
    }
    return `${originalTopic}/response`;
  };

  const handleSendMessage = () => {
    if (topic.trim() && message.trim()) {
      console.log('Sending message:', message, 'to topic:', topic);

      try {
        const responseTopic = getResponseTopic(topic);
        subscribe(responseTopic);
        publish(topic, message);

        setPrimaryMessages(prev => {
          // Add request message at the beginning
          const newMessages = [
            {
              topic: topic,
              payload: message,
              timestamp: new Date().toISOString()
            },
            ...prev
          ];
          return newMessages.slice(0, 1); // Keep first 30 messages
        });
        setMessage('');
      } catch (error) {
        console.error('Failed to send message:', error);
        setConnectionStatus('error');
      }
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Alert
        severity={connectionStatus === 'connected' ? 'success' : 'warning'}
        sx={{ mb: 3 }}
      >
        Connection Status: {connectionStatus}
      </Alert>

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
                // variant="contained"
                onClick={handleSendMessage}
                endIcon={<SendIcon />}
                size='small'
              >
                Send
              </Button>
            </Stack>
          </Stack>
        </CardContent>
      </Card>

      <Grid container spacing={3}>
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

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Secondary Messages
              </Typography>
              <Stack spacing={2}>
                {secondaryMessages.map((msg, index) => (
                  <Paper
                    key={index}
                    elevation={0}
                    sx={{
                      p: 2,
                      border: '1px solid',
                      borderColor: 'divider'
                    }}
                  >
                    <Typography variant="subtitle2" gutterBottom>
                      {msg.topic}
                    </Typography>
                    <Typography variant="body2">
                      {msg.payload}
                    </Typography>
                  </Paper>
                ))}
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
