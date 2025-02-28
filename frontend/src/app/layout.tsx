// 'use client';
import * as React from 'react';
import { NextAppProvider } from '@toolpad/core/nextjs';
import { AppRouterCacheProvider } from '@mui/material-nextjs/v15-appRouter';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import LayersIcon from '@mui/icons-material/Layers';
import DescriptionIcon from '@mui/icons-material/Description';

import type { Navigation } from '@toolpad/core/AppProvider';
import { SessionProvider, signIn, signOut } from 'next-auth/react';
import { auth } from '../auth';
import theme from '../theme';
import Description from '@mui/icons-material/Description';

const NAVIGATION: Navigation = [
  // {
  //   kind: 'header',
  //   title: 'Monitor',
  // },
  {
    title: 'Dashboard',
    icon: <DashboardIcon />,
  },
  {
    segment: 'orders',
    title: 'Orders',
    icon: <ShoppingCartIcon />,
  },
  {
    segment: 'equipment',
    title: 'Equipments',
    icon: <LayersIcon />,
    children: [
      {
        segment: 'monitor',
        title: 'Monitor',
        icon: <DescriptionIcon />,
      },
      {
        segment: 'config',
        title: 'Config',
        icon: <DescriptionIcon />,
      },
      {
        segment: 'control',
        title: 'Control',
        icon: <DescriptionIcon />,
      },
    ]
  },
  {
    segment: 'secsgem',
    title: 'SecsGem',
    icon: <Description />,
    children: [
      {
        segment: 'monitor',
        title: 'Monitor',
        icon: <DescriptionIcon />,
      },
      {
        segment: 'config',
        title: 'Config',
        icon: <DescriptionIcon />,
        children: [
          {
            segment: "equipment",
            title: "equipments",
            icon: <DescriptionIcon />,
          },
          {
            segment: "validate",
            title: "validate config",
            icon: <DescriptionIcon />,
          }
        ]
      },
      {
        segment: 'control',
        title: 'Control',
        icon: <DescriptionIcon />,
      },
    ]
  },
  {
    segment: 'datalot',
    title: 'Data lot',
    icon: <ShoppingCartIcon />,
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
    <html lang="en" data-toolpad-color-scheme="light">
      <head>
        {/* <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {

                  const defaultMode = typeof window !== 'undefined' ? localStorage.getItem('mui-mode') || 'dark' : 'dark';
                  console.log('defaultMode', defaultMode);

                  const mode = localStorage.getItem('mui-mode');
                  console.log('current mode', mode);

                  if (mode) {
                    document.documentElement.setAttribute('data-mui-color-scheme', mode);
                  }
                } catch (e) {}
              })();
            `,
          }}
        /> */}
      </head>
      <body>
        <SessionProvider session={session}>
          <AppRouterCacheProvider options={{ enableCssLayer: true }}>
            <NextAppProvider
              theme={theme}
              navigation={NAVIGATION}
              branding={BRANDING}
              session={session}
              authentication={AUTHENTICATION}
            >
              {props.children}
            </NextAppProvider>
          </AppRouterCacheProvider>
        </SessionProvider>

      </body>
    </html>
  );
}
