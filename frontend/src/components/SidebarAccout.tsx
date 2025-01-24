'use client'
import { Avatar } from '@mui/material';
import { Account } from '@toolpad/core';
import React from 'react'

export default function CustomSidebarAccount() {
    return (
        <Account
            slotProps={{
                signInButton: {
                    color: 'inherit',
                },
                preview: {
                    variant: 'expanded',
                },
            }
            }
        />
    )
}
export function SidebarAccountOverride() {
    return null;
}