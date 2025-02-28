import React, { useEffect, useState } from 'react';
import { Container, Typography, Box } from '@mui/material';
import ConfigList from '../../components/ConfigList';
import { getConfigs } from '../../services/api';

const ConfigIndex = () => {
    const [configs, setConfigs] = useState([]);

    useEffect(() => {
        const fetchConfigs = async () => {
            const data = await getConfigs();
            setConfigs(data);
        };

        fetchConfigs();
    }, []);

    return (
        <Container>
            <Box my={4}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Configurations
                </Typography>
                <ConfigList configs={configs} />
            </Box>
        </Container>
    );
};

export default ConfigIndex;