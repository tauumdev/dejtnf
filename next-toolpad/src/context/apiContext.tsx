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
    get: (id: string) => Promise<any>;
    gets: () => Promise<any>;
    // create: (data: any) => Promise<any>;
    // update: (id: string, data: any) => Promise<any>;
    // delete: (id: string) => Promise<any>;
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
    const logIn = async (user: { email: string; password: string }) => {
        return await login(user);
    };

    useEffect(() => {
        get_equipments();
    }, [])

    // eqquipment
    const get_equipments = async () => {
        setLoading(true);
        try {
            const response: EquipmentResponse = await getEquipments();
            setEquipmentList(response.docs);
            return response.docs;
        }
        catch (error) {
            console.error('Error fetching equipments:', error);
        }
        setLoading(false);
    };

    const get_equipment = async (id: string) => {
        try {
            const response: Equipment = await getEquipment(id);
            console.log('Equipment:', response);
            return response;
        } catch (error) {
            console.error('Error fetching equipment:', error);
            throw error;
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
                    get: get_equipment,
                    gets: get_equipments,

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
