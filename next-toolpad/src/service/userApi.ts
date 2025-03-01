import axios from "axios";

const API_HOST = process.env.REACT_APP_API_HOST || "http://localhost:3000";

// console.log('API_HOST:', API_HOST);

// Register a new user
export const register = async (user: any) => {
    try {
        const response = await axios.post(`${API_HOST}/register`, user);
        return response.data;
    }
    catch (error) {
        console.error('Register Error:', error);
        return null;
    }
}

// Verify a user
export const verify = async (user: any) => {
    try {
        const response = await axios.post(`${API_HOST}/verify`, user);
        return response.data;
    }
    catch (error) {
        console.error('Verify Error:', error);
        return null;
    }
}

// Forgot password
export const forgot = async (user: any) => {
    try {
        const response = await axios.post(`${API_HOST}/forgot`, user);
        return response.data;
    }
    catch (error) {
        console.error('Forgot Error:', error);
        return null;
    }
}

// Reset password
export const reset = async (user: any) => {
    try {
        const response = await axios.post(`${API_HOST}/reset`, user);
        return response.data;
    }
    catch (error) {
        console.error('Reset Error:', error);
        return null;
    }
}

// Login
export const login = async (user: any) => {
    try {
        const response = await axios.post(`${API_HOST}/login`, user);
        return response.data;
    }
    catch (error) {
        console.error('Login Error:', error);
        return null;
    }
}

// Get token
export const token = async () => {
    try {
        const response = await axios.get(`${API_HOST}/token`);
        return response.data;
    }
    catch (error) {
        console.error('Token Error:', error);
        return null;
    }
}

// Users

// Get all users
export const getUsers = async () => {
    try {
        const response = await axios.get(`${API_HOST}/users`);
        return response.data;
    }
    catch (error) {
        console.error('Get Users Error:', error);
        return null;
    }
}

// Get user by ID
export const getUserById = async (id: string) => {
    try {
        const response = await axios.get(`${API_HOST}/users/${id}`);
        return response.data;
    }
    catch (error) {
        console.error('Get User by ID Error:', error);
        return null;
    }
}

// Create a new user
export const createUser = async (user: any) => {
    try {
        const response = await axios.post(`${API_HOST}/users`, user);
        return response.data;
    }
    catch (error) {
        console.error('Create User Error:', error);
        return null;
    }
}

// Update a user
export const updateUser = async (id: string, user: any) => {
    try {
        const response = await axios.put(`${API_HOST}/users/${id}`, user);
        return response.data;
    }
    catch (error) {
        console.error('Update User Error:', error);
        return null;
    }
}

// Delete a user
export const deleteUser = async (id: string) => {
    try {
        const response = await axios.delete(`${API_HOST}/users/${id}`);
        return response.data;
    }
    catch (error) {
        console.error('Delete User Error:', error);
        return null;
    }
}
