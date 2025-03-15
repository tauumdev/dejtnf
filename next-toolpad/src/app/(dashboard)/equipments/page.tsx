import React, { use } from 'react'
import { auth } from '../../api/auth/auth';
import SecsGemEquipments from '@/src/components/equipment';

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
        <SecsGemEquipments user={user} />
    )
}
