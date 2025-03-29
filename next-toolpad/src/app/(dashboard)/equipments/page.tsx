import React, { use } from 'react'
import { auth } from '../../api/auth/auth';
// import SecsGemEquipments from '@/src/components/equipment';
import ValidateConfigComponent from '@/src/components/validate';
import { Divider, Grid2 } from '@mui/material';

interface User {
    name: string;
    email: string;
    role: string;
}

export default async function EquipmentPage() {
    const session = await auth();

    const user: User = {
        name: '',
        email: '',
        role: ''
    }

    user.name = session?.user?.name ?? 'Default Name';
    user.email = session?.user?.email ?? 'default@example.com';
    user.role = session?.user?.role ?? 'defaultRole';

    return (
        <Grid2 spacing={2}>
            {/* <SecsGemEquipments user={user} /> */}
            {/* <Divider sx={{ my: 2 }} /> */}
            <ValidateConfigComponent user={user} />
        </Grid2>
    )
}
