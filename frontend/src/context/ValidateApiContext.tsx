'use client';
import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import axios from 'axios';

const API_URL_VALIDATE_CONFIG = 'http://localhost:3000/api/validate';

interface Config {
    _id: string;
    equipment_name: string;
    config: any[];
}

interface ApiContextType {
    configs: Config[];
    loading: boolean;
    fetchConfigs: () => Promise<void>;
    getConfigById: (id: string) => Promise<Config | null>;
    createConfig: (config: Config) => Promise<boolean>;
    updateConfig: (id: string, config: Config) => Promise<boolean>;
    deleteConfig: (id: string) => Promise<boolean>;
}

const ApiContext = createContext<ApiContextType | undefined>(undefined);

export function ApiProvider({ children }: { children: ReactNode }) {
    const [configs, setConfigs] = useState<Config[]>([]);
    const [loading, setLoading] = useState<boolean>(true);

    useEffect(() => {
        fetchConfigs();
    }, []);

    const fetchConfigs = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`${API_URL_VALIDATE_CONFIG}/configs?limit=100&sort=equipment_name&order=1`);
            setConfigs(response.data);
        } catch (error) {
            console.error('Error fetching configs:', error);
        }
        setLoading(false);
    };

    const getConfigById = async (id: string): Promise<Config | null> => {
        try {
            const response = await axios.get(`${API_URL_VALIDATE_CONFIG}/config/${id}`);
            return response.data;
        } catch (error) {
            console.error(`Error fetching config ${id}:`, error);
            return null;
        }
    };

    const createConfig = async (config: Config): Promise<boolean> => {
        try {
            const response = await axios.post(`${API_URL_VALIDATE_CONFIG}/config`, config);
            setConfigs([...configs, response.data]);
            return true;
        } catch (error) {
            console.error('Error creating config:', error);
            return false;
        }
    };

    const updateConfig = async (id: string, config: Config): Promise<boolean> => {
        try {
            const response = await axios.put(`${API_URL_VALIDATE_CONFIG}/config/${id}`, config);
            setConfigs(configs.map((c) => (c._id === id ? response.data : c)));
            return true;
        } catch (error) {
            console.error(`Error updating config ${id}:`, error);
            return false;
        }
    };

    const deleteConfig = async (id: string): Promise<boolean> => {
        try {
            await axios.delete(`${API_URL_VALIDATE_CONFIG}/config/${id}`);
            setConfigs(configs.filter((c) => c._id !== id));
            return true;
        } catch (error) {
            console.error(`Error deleting config ${id}:`, error);
            return false;
        }
    };

    return (
        <ApiContext.Provider value={{ configs, loading, fetchConfigs, getConfigById, createConfig, updateConfig, deleteConfig }}>
            {children}
        </ApiContext.Provider>
    );
}

export function UseApi() {
    const context = useContext(ApiContext);
    if (!context) {
        throw new Error('ValidateApi must be used within a DejtnfApiProvider');
    }
    return context;
}
