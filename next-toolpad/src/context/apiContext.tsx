'use client';
import React, { createContext, useContext, useEffect, useState } from 'react';
import { login } from '../service/userApi';
import { getEquipment, getEquipments, createEquipment, deleteEquipment, updateEquipment } from '../service/equipmentApi';
import { getLotValidateConfigs } from '../service/validateApi';

import { EquipmentResponse, Equipment } from '../service/types';

interface UserContextProps {
    logIn: (user: { email: string; password: string }) => Promise<any>;
}

interface ValidateContextProps {
    getLotValidateConfigs: () => Promise<any>;
}

interface EquipmentContextProps {
    loading: boolean;
    list: Equipment[];
    totalCount: number; // Add this
    get: (id: string) => Promise<any>;
    gets: (
        filter?: string,
        fields?: string[],
        page?: number,
        limit?: number,
        sort?: string,
        order?: number
    ) => Promise<any>;
    create: (data: Equipment) => Promise<any>;
    update: (id: string, data: any) => Promise<any>;
    delete: (id: string) => Promise<any>;
}

interface ApiContextProps {
    user: UserContextProps;
    validate: ValidateContextProps;
    equipment: EquipmentContextProps;
}

const ApiContext = createContext<ApiContextProps | undefined>(undefined);

export const ApiProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [equipmentList, setEquipmentList] = useState<Equipment[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [totalCount, setTotalCount] = useState<number>(0); // Add this

    const logIn = async (user: { email: string; password: string }) => {
        return await login(user);
    };

    const get_equipments = async (
        filter?: string,
        fields?: string[],
        page: number = 1,
        limit: number = 20,
        sort?: string,
        order: number = 1
    ) => {
        setLoading(true);
        try {
            const response: EquipmentResponse = await getEquipments(filter, fields, page, limit, sort, order);
            setEquipmentList(response.docs);
            setTotalCount(response.totalDocs); // Assuming API returns totalDocs
            return response;
        } catch (error) {
            console.error('Error fetching equipments:', error);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    return (
        <ApiContext.Provider
            value={{
                user: { logIn },
                validate: { getLotValidateConfigs },
                equipment: {
                    loading: loading,
                    list: equipmentList,
                    totalCount: totalCount,
                    create: createEquipment,
                    get: getEquipment,
                    gets: get_equipments,
                    delete: deleteEquipment,
                    update: updateEquipment,
                },
            }}
        >
            {children}
        </ApiContext.Provider>
    );
};

export const useApiContext = () => {
    const context = useContext(ApiContext);
    if (!context) {
        throw new Error('useApiContext must be used within an ApiProvider');
    }
    return context;
};
