import * as React from 'react';
import Typography from '@mui/material/Typography';

import { Box } from '@mui/material';
import { auth } from '@/src/app/api/auth/auth';


export default async function EquipmentControl() {
    const session = await auth();
    // const jwt = await auth();
    // console.log(jwt);
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
        <Box>
            <Box>
                <Typography>
                    Welcome to Toolpad, {session?.user?.name || 'User'}!
                </Typography>
                <Typography>
                    Your role: {session?.user?.role || 'Unknown'}
                </Typography>
                {/* <pre>{JSON.stringify(session, null, 2)}</pre> */}
                {/* <pre>{JSON.stringify(jwt, null, 2)}</pre> */}
            </Box>
        </Box>
    );
}
