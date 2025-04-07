import * as React from 'react';
import { NextAppProvider } from '@toolpad/core/nextjs';
import { AppRouterCacheProvider } from '@mui/material-nextjs/v15-appRouter';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import BrokenImageIcon from '@mui/icons-material/BrokenImage';
import type { Navigation } from '@toolpad/core/AppProvider';
import { SessionProvider, signIn, signOut } from 'next-auth/react';
import { auth } from './api/auth/auth';
import theme from '../theme/theme';

import { ApiProvider } from '../../src/context/apiContext';
import { MqttProvider } from '../context/MqttContext';

const NAVIGATION: Navigation = [
  {
    segment: '',
    title: 'Dashboard',
    icon: <DashboardIcon />,
  },
  {
    segment: 'earthquake',
    title: 'Earthquake',
    icon: <BrokenImageIcon />,
  },
  {
    segment: 'equipments',
    title: 'Equipments',
    icon: <ShoppingCartIcon />,
    children: [
      {
        segment: 'monitor',
        title: 'Monitor',
        icon: <DashboardIcon />,
      },
      {
        segment: 'config',
        title: 'Config',
        icon: <DashboardIcon />,
      },
    ]
  },
];

const BRANDING = {
  title: 'dejtnf',
};

const AUTHENTICATION = {
  signIn,
  signOut,
};

export default async function RootLayout(props: { children: React.ReactNode }) {
  const session = await auth();

  return (
    <html lang="en" data-toolpad-color-scheme="light" suppressHydrationWarning>
      <body>
        <SessionProvider session={session}>
          <AppRouterCacheProvider options={{ enableCssLayer: true }}>

            <MqttProvider>
              <ApiProvider>
                <NextAppProvider
                  navigation={NAVIGATION}
                  branding={BRANDING}
                  session={session}
                  authentication={AUTHENTICATION}
                  theme={theme}
                >
                  {props.children}
                </NextAppProvider>
              </ApiProvider>
            </MqttProvider>

          </AppRouterCacheProvider>
        </SessionProvider>
      </body>
    </html>
  );
}
