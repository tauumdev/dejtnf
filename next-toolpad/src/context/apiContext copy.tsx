'use client';
import React, { createContext, useContext, useState, useEffect } from 'react';
import { login } from '../dejtnf-api/user';

interface UserContextProps {
    logIn: (user: any) => Promise<any>;
    // // users: any[];
    // // fetchUsers: () => void;
    // getUser: (id: string) => Promise<any>;
    // addUser: (user: any) => Promise<any>;
    // editUser: (id: string, user: any) => Promise<any>;
    // removeUser: (id: string) => Promise<any>;
}

interface userContextProps { }
interface validateContextProps { }
interface equipmentContextProps { }

interface apiContextProps {
    user: userContextProps;
    validate: validateContextProps;
    equipment: equipmentContextProps;
}

const UserContext = createContext<UserContextProps | undefined>(undefined);

export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {

    const logIn = async (user: any) => {
        const response = await login(user);
        console.log(response);
        return response;
    };

    return (
        <UserContext.Provider value={{ logIn }}>
            {children}
        </UserContext.Provider>
    );
};

export const useUserContext = () => {
    const context = useContext(UserContext);
    if (context === undefined) {
        throw new Error('useUserContext must be used within a UserProvider');
    }
    return context;
};