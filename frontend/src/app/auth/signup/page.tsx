"use client";
import React, { useState } from 'react';
import {
    Container,
    Paper,
    Typography,
    TextField,
    Button,
    Link,
    Box
} from '@mui/material';
import { useRouter } from 'next/navigation';

export default function SignUp() {
    const [name, setName] = useState('');
    const [en, setEn] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');
    const router = useRouter();
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setMessage('');

        try {
            const response = await fetch('http://localhost:3000/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name,
                    en,
                    email,
                    password
                })
            });

            if (!response.ok) {
                const errData = await response.json();
                console.log(errData.errors.msg);
                throw new Error(errData.errors.msg || 'Signup failed');
                // throw new Error(errData.error || 'Signup failed');
            }

            const data = await response.json();
            setMessage('Signup successful! Please check your email for confirmation.');
            router.push('/auth/signin');
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="sm" sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh'
        }}>
            <Paper sx={{ padding: 4, width: '100%' }}>
                <Typography variant="h4" component="h1" gutterBottom align="center">
                    Welcome 👋
                </Typography>
                <Typography variant="body1" align="center" gutterBottom>
                    Sign up for an account.
                </Typography>
                {error && (
                    <Typography color="error" align="center">
                        {error}
                    </Typography>
                )}
                {message && (
                    <Typography color="success.main" align="center">
                        {message}
                    </Typography>
                )}
                <Box component="form" onSubmit={handleSubmit} noValidate sx={{
                    mt: 2,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 2
                }}>
                    <TextField
                        label="Name"
                        variant="outlined"
                        fullWidth
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                    />
                    <TextField
                        label="En"
                        variant="outlined"
                        fullWidth
                        value={en}
                        onChange={(e) => setEn(e.target.value)}
                    />
                    <TextField
                        label="Email"
                        type="email"
                        variant="outlined"
                        fullWidth
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                    <TextField
                        label="Password"
                        type="password"
                        variant="outlined"
                        fullWidth
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <Button type="submit" variant="contained" disabled={loading} fullWidth>
                        {loading ? 'Creating account...' : 'Create account'}
                    </Button>
                </Box>
                <Box sx={{ mt: 2, textAlign: 'center' }}>
                    <Typography variant="body2">
                        Already have an account? <Link href="/auth/signin">Log in</Link>
                    </Typography>
                </Box>
            </Paper>
        </Container>
    );
}
