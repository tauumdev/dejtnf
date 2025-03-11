'use client';
import React, { createContext, useContext, useEffect, useState } from 'react';
import { login } from '../service/userApi';
import { getEquipment, getEquipments, createEquipment, deleteEquipment, updateEquipment } from '../service/equipmentApi';
import { getValidateConfigs, getValidateConfig, createLotValidateConfig, updateLotValidateConfig, deleteLotValidateConfig } from '../service/validateApi';

import { EquipmentResponse, Equipment, ValidateConfigPropTypes, ValidateResponse, ConfigItem } from '../service/types';

interface UserContextProps {
    logIn: (user: { email: string; password: string }) => Promise<any>;
}

interface ValidateContextProps {
    loading: boolean;
    list: ValidateConfigPropTypes[];
    totalCount: number;
    get: (id: string) => Promise<any>;
    gets: (
        filter?: string,
        fields?: string[],
        page?: number,
        limit?: number,
        sort?: string,
        order?: number
    ) => Promise<any>;
    create: (data: ConfigItem) => Promise<any>;
    update: (id: string, data: any) => Promise<any>;
    delete: (id: string) => Promise<any>;
}

interface EquipmentContextProps {
    loading: boolean;
    list: Equipment[];
    totalCount: number;
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
    const [loadingEquipment, setLoadingEquipment] = useState(true)
    const [totalCountEquipment, setTotalCountEquipment] = useState<number>(0)

    const [validateList, setValidateList] = useState<ValidateConfigPropTypes[]>([])
    const [loadingValidateConfig, setLoadingValidateConfig] = useState(true)
    const [totalCountValidateConfig, setTotalCountValidateConfig] = useState<number>(0)


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
        setLoadingEquipment(true);
        try {
            const response: EquipmentResponse = await getEquipments(filter, fields, page, limit, sort, order);
            setEquipmentList(response.docs);
            setTotalCountEquipment(response.totalDocs); // Assuming API returns totalDocs
            return response;
        } catch (error) {
            console.error('Error fetching equipments:', error);
            throw error;
        } finally {
            setLoadingEquipment(false);
        }
    };

    const get_validateConfigs = async (
        filter?: string,
        fields?: string[],
        page: number = 1,
        limit: number = 20,
        sort?: string,
        order: number = 1
    ) => {
        setLoadingValidateConfig(true);
        try {
            const response: ValidateResponse = await getValidateConfigs(filter, fields, page, limit, sort, order);
            setValidateList(response.docs);
            setTotalCountValidateConfig(response.totalDocs); // Assuming API returns totalDocs
            return response;
        } catch (error) {
            console.error('Error fetching validate configs:', error);
            throw error;
        } finally {
            setLoadingValidateConfig(false);
        }
    };

    return (
        <ApiContext.Provider
            value={{
                user: { logIn },
                validate: {
                    loading: loadingValidateConfig,
                    list: validateList,
                    totalCount: totalCountValidateConfig,
                    get: getValidateConfig,
                    gets: get_validateConfigs,
                    create: createLotValidateConfig,
                    update: updateLotValidateConfig,
                    delete: deleteLotValidateConfig
                },
                equipment: {
                    loading: loadingEquipment,
                    list: equipmentList,
                    totalCount: totalCountEquipment,
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
