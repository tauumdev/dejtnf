import axios from "axios";

const API_HOST = process.env.REACT_APP_API_HOST || "http://localhost:3000";

// Lot Validate Config

// Get all Lot Validate Config records
export const getLotValidateConfigs = async () => {
    try {
        const response = await axios.get(`${API_HOST}/api/validate/configs`);
        return response.data;
    }
    catch (error) {
        console.error('Get Lot Validate Configs Error:', error);
        return null;
    }
}

// Get Lot Validate Config by ID
export const getLotValidateConfig = async (id: string) => {
    try {
        const response = await axios.get(`${API_HOST}/api/validate/config/${id}`);
        return response.data;
    }
    catch (error) {
        console.error('Get Lot Validate Config by ID Error:', error);
        return null;
    }
}

// Create a new Lot Validate Config record
export const createLotValidateConfig = async (lotValidateConfig: any) => {
    try {
        const response = await axios.post(`${API_HOST}/api/validate/config`, lotValidateConfig);
        return response.data;
    }
    catch (error) {
        console.error('Create Lot Validate Config Error:', error);
        return null;
    }
}

// Update a Lot Validate Config record
export const updateLotValidateConfig = async (id: string, lotValidateConfig: any) => {
    try {
        const response = await axios.put(`${API_HOST}/api/validate/config/${id}`, lotValidateConfig);
        return response.data;
    }
    catch (error) {
        console.error('Update Lot Validate Config Error:', error);
        return null;
    }
}

// Delete a Lot Validate Config record
export const deleteLotValidateConfig = async (id: string) => {
    try {
        const response = await axios.delete(`${API_HOST}/api/validate/config/${id}`);
        return response.data;
    }
    catch (error) {
        console.error('Delete Lot Validate Config Error:', error);
        return null;
    }
}

