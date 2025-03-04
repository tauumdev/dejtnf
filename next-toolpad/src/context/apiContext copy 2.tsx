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

// In your ApiContext interface, add totalCount
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

    // useEffect(() => {
    //     get_equipments(undefined, undefined, 1, 20, 'equipment_name', 1);
    // }, [])

    const create_equipment = async (equipment: Equipment) => {
        createEquipment(equipment)
    }

    // const get_equipments = async (
    //     filter?: string,
    //     fields?: string[],
    //     page: number = 1,
    //     limit: number = 20,
    //     sort?: string,
    //     order: number = 1
    // ) => {
    //     setLoading(true);
    //     try {
    //         const response: EquipmentResponse = await getEquipments(filter, fields, page, limit, sort, order);
    //         setEquipmentList(response.docs);
    //         return response.docs;
    //     } catch (error) {
    //         console.error('Error fetching equipments:', error);
    //     } finally {
    //         setLoading(false); // Ensure loading is always set to false
    //     }
    // };

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

    const get_equipment = async (id: string) => {
        try {
            const response: Equipment = await getEquipment(id);
            return response;
        } catch (error) {
            console.error('Error fetching equipment:', error);
            throw error;
        }
    };
    const del_equipment = async (id: string) => {
        try {
            const response = await deleteEquipment(id);
            return response;
        } catch (error) {
            console.error('Error delete equipment:', error);
            throw error;
        }
    };


    const update_equipment = async (id: string, equipment: Partial<Equipment>) => {
        try {
            const response: Equipment = await updateEquipment(id, equipment);
            return response;
        } catch (error) {
            console.log("Error update equipment:", error);
            throw error;
        }
    }
    return (
        <ApiContext.Provider
            value={{
                user: { logIn },
                validate: { getLotValidateConfigs },
                equipment: {
                    loading: loading,
                    list: equipmentList,
                    create: create_equipment,
                    get: get_equipment,
                    gets: get_equipments,
                    delete: del_equipment,
                    update: update_equipment,
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
