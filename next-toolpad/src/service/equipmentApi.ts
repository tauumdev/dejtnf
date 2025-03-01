import axios from "axios";
import { EquipmentResponse, Equipment } from '../service/types';
const API_HOST = process.env.REACT_APP_API_HOST || "http://localhost:3000";

// interface Equipment {
//     id?: string;
//     name: string;
//     type: string;
//     status?: string;
// }

// Get all equipments
export const getEquipments = async (): Promise<EquipmentResponse> => {
    try {
        const response = await axios.get(`${API_HOST}/api/secsgem/equipments`);
        return response.data;
    } catch (error) {
        console.error("Get Equipments Error:", error);
        throw error;
    }
};


// // Get all equipments
// export const getEquipments = async (): Promise<Equipment[]> => {
//     try {
//         const response = await axios.get(`${API_HOST}/api/secsgem/equipments`);
//         return response.data;
//     } catch (error) {
//         console.error("Get Equipments Error:", error);
//         throw error;
//     }
// };

// Get equipment by ID
export const getEquipment = async (id: string): Promise<Equipment> => {
    try {
        const response = await axios.get(`${API_HOST}/api/secsgem/equipment/${id}`);
        return response.data;
    } catch (error) {
        console.error("Get Equipment by ID Error:", error);
        throw error;
    }
};

// Create a new equipment
export const createEquipment = async (equipment: Equipment): Promise<Equipment> => {
    try {
        const response = await axios.post(`${API_HOST}/api/secsgem/equipment`, equipment);
        return response.data;
    } catch (error) {
        console.error("Create Equipment Error:", error);
        throw error;
    }
};

// Update an equipment
export const updateEquipment = async (id: string, equipment: Partial<Equipment>): Promise<Equipment> => {
    try {
        const response = await axios.put(`${API_HOST}/api/secsgem/equipment/${id}`, equipment);
        return response.data;
    } catch (error) {
        console.error("Update Equipment Error:", error);
        throw error;
    }
};

// Delete an equipment
export const deleteEquipment = async (id: string): Promise<{ success: boolean }> => {
    try {
        const response = await axios.delete(`${API_HOST}/api/secsgem/equipment/${id}`);
        return response.data;
    } catch (error) {
        console.error("Delete Equipment Error:", error);
        throw error;
    }
};
