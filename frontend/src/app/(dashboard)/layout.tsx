// 'use client'
import * as React from 'react';
import { DashboardLayout } from '@toolpad/core/DashboardLayout';
import { PageContainer } from '@toolpad/core/PageContainer';
import CustomSidebarAccount, { SidebarAccountOverride } from '../../components/SidebarAccout';
import { MqttProvider } from '../../context/MqttContext';
import { ApiProvider } from '../../context/ValidateApiContext';
export default async function DashboardPagesLayout(props: { children: React.ReactNode }) {
  return (
    <DashboardLayout
      sidebarExpandedWidth={240}
      slots={{
        toolbarAccount: SidebarAccountOverride,
        sidebarFooter: CustomSidebarAccount
      }}
    >
      <ApiProvider>
        <MqttProvider>
          <PageContainer>{props.children}</PageContainer>
        </MqttProvider>
      </ApiProvider>
    </DashboardLayout>
  );
}
