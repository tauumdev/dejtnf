// 'use client'
import Typography from '@mui/material/Typography';

import { Box, Button, Card, CardContent, Divider, Grid } from '@mui/material';
import { auth } from '@/src/app/api/auth/auth';

// import { useApiContext } from '@/src/context/apiContext';
import EquipmentList from '../../../../components/secsgem/equipmentList'
import ValidateConfig_component from '@/src/components/secsgem/validate/validateConfig';
import CollapValidate from '@/src/components/secsgem/validate/collapValidate';

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
            <Divider sx={{ p: 2 }} />
            {/* <ValidateConfig_component /> */}
            <CollapValidate />
            {/* <ValidateConfig_component /> */}
        </div>

    );
}
