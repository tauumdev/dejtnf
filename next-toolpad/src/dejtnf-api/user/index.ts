import axios from 'axios';

const API_HOST = process.env.NEXT_PUBLIC_API_URL

export const register = async (user: any) => {
    const response = await axios.post(`${API_HOST}/register`, user);
    // console.log(response);
    return response.data;
}

export const verify = async (user: any) => {
    const response = await axios.post(`${API_HOST}/verify`, user);
    // console.log(response);
    return response.data;
}

export const forgot = async (user: any) => {
    const response = await axios.post(`${API_HOST}/forgot`, user);
    // console.log(response);
    return response.data;
}

export const reset = async (user: any) => {
    const response = await axios.post(`${API_HOST}/reset`, user);
    // console.log(response);
    return response.data;
}

export const login = async (user: any) => {
    try {
        const response = await axios.post(`${API_HOST}/login`, user);
        return response.data; // Ensure this returns the correct data
    } catch (error) {
        console.error('Login Error:', error);
        return null; // Handle errors gracefully
    }
};


export const token = async () => {
    const response = await axios.get(`${API_HOST}/token`);
    // console.log(response);
    return response.data;
}

export const getUsers = async () => {
    const response = await axios.get(`${API_HOST}/users`);
    // console.log(response);
    return response.data;
}

export const getUserById = async (id: string) => {
    const response = await axios.get(`${API_HOST}/users/${id}`);
    // console.log(response);
    return response.data;
}

export const createUser = async (user: any) => {
    const response = await axios.post(`${API_HOST}/users`, user);
    // console.log(response);
    return response.data;
}

export const updateUser = async (id: string, user: any) => {
    const response = await axios.put(`${API_HOST}/users/${id}`, user);
    // console.log(response);
    return response.data;
}

export const deleteUser = async (id: string) => {
    const response = await axios.delete(`${API_HOST}/users/${id}`);
    // console.log(response);
    return response.data;
}