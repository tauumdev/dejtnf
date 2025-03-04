import axios from "axios";
import { EquipmentResponse, Equipment } from '../service/types';

const API_HOST = process.env.REACT_APP_API_HOST || "http://localhost:3000";

// Define axios instance
const api = axios.create({
    baseURL: `${API_HOST}/api/secsgem`,
    headers: { 'Content-Type': 'application/json' },
});

// Get equipments
export const getEquipments = async (
    filter?: string,
    fields?: string[],
    page: number = 1,
    limit: number = 20,
    sort?: string,
    order: number = 1
): Promise<EquipmentResponse> => {
    try {
        const response = await api.get('/equipments', {
            params: {
                filter,
                fields: fields?.join(','),
                page,
                limit,
                sort,
                order,
            },
        });
        return response.data;
    } catch (error: any) {
        console.error("Get Equipments Error:", error.response?.data || error.message);
        throw error;
    }
};

// Get equipment by id
export const getEquipment = async (id: string): Promise<Equipment> => {
    try {
        const response = await api.get(`/equipment/${id}`);
        return response.data;
    } catch (error: any) {
        throw new Error(error.response?.data?.errors?.msg || `Failed to fetch equipment with ID: ${id}`);
    }
};

// Create equipment 
export const createEquipment = async (equipment: Equipment): Promise<Equipment> => {
    try {
        const response = await api.post('/equipment', equipment);
        return response.data;
    } catch (error: any) {
        throw new Error(error.response?.data?.errors?.msg || "Failed to create equipment");
    }
};

// Update equipment
export const updateEquipment = async (id: string, equipment: Partial<Equipment>): Promise<Equipment> => {
    try {
        const response = await api.put(`/equipment/${id}`, equipment);
        return response.data;
    } catch (error: any) {
        throw new Error(error.response?.data?.errors?.msg || `Failed to update equipment with ID: ${id}`);
    }
};

// Delete equipment
export const deleteEquipment = async (id: string): Promise<{ success: boolean }> => {
    try {
        const response = await api.delete(`/equipment/${id}`);
        return response.data;
    } catch (error: any) {
        throw new Error(error.response?.data?.errors?.msg || `Failed to delete equipment with ID: ${id}`);
    }
};