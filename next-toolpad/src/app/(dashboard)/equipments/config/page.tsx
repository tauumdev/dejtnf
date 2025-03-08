// 'use client'
import Typography from '@mui/material/Typography';

import { Box, Button, Card, CardContent, Grid } from '@mui/material';
import { auth } from '@/src/app/api/auth/auth';

// import { useApiContext } from '@/src/context/apiContext';
import EquipmentList from '../../../../components/secsgem/equipmentList'

export default async function EquipmentControl() {
    const session = await auth();

    if (session?.user?.role !== 'admin') {
        return (
            <Box>
                <Typography>
                    You are not authorized to access this page.
                </Typography>
            </Box>
        );
    }

    return (
        <div>
            <EquipmentList />
        </div>

    );
}
