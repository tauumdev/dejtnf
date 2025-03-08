import axios from "axios";
import { ValidateResponse, ValidateConfigPropTypes, ValidateAllowToolId, ValidateDataWithSelectionCode, ValidateOptions } from "./types";

const API_HOST = process.env.REACT_APP_API_HOST || "http://localhost:3000";

// Define axios instance
const api = axios.create({
    baseURL: `${API_HOST}/api/validate`,
    headers: { 'Content-Type': 'application/json' },
});

// Get all Lot Validate Config records
export const getValidateConfigs = async (
    filter?: string,
    fields?: string[],
    page: number = 1,
    limit: number = 20,
    sort?: string,
    order: number = 1
): Promise<ValidateResponse> => {
    try {
        const response = await api.get('/configs', {
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
        console.error("Get Validates Error:", error.response?.data || error.message);
        throw error;
    }
};



// Get Lot Validate Config by ID
export const getValidateConfig = async (id: string): Promise<ValidateConfigPropTypes> => {
    try {
        const response = await api.get(`/config/${id}`);
        return response.data;
    } catch (error: any) {
        throw new Error(error.response?.data?.errors?.msg || `Failed to fetch validate config with ID: ${id}`);
    }
}

// // Create a new Lot Validate Config record
// export const createLotValidateConfig = async (lotValidateConfig: any) => {
//     try {
//         const response = await axios.post(`${API_HOST}/api/validate/config`, lotValidateConfig);
//         return response.data;
//     }
//     catch (error) {
//         console.error('Create Lot Validate Config Error:', error);
//         return null;
//     }
// }

// // Update a Lot Validate Config record
// export const updateLotValidateConfig = async (id: string, lotValidateConfig: any) => {
//     try {
//         const response = await axios.put(`${API_HOST}/api/validate/config/${id}`, lotValidateConfig);
//         return response.data;
//     }
//     catch (error) {
//         console.error('Update Lot Validate Config Error:', error);
//         return null;
//     }
// }

// // Delete a Lot Validate Config record
// export const deleteLotValidateConfig = async (id: string) => {
//     try {
//         const response = await axios.delete(`${API_HOST}/api/validate/config/${id}`);
//         return response.data;
//     }
//     catch (error) {
//         console.error('Delete Lot Validate Config Error:', error);
//         return null;
//     }
// }

