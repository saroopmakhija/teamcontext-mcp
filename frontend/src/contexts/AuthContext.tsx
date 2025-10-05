'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '@/types/auth';
import { authAPI } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<string>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const userData = localStorage.getItem('user');
        if (userData) {
          // Verify with backend that the session is still valid
          try {
            const userInfo = await authAPI.getCurrentUser();
            const validatedUser: User = {
              id: userInfo.id,
              email: userInfo.email,
              name: userInfo.name,
              created_at: userInfo.created_at,
            };
            
            localStorage.setItem('user', JSON.stringify(validatedUser));
            setUser(validatedUser);
          } catch (error) {
            // Session invalid, clear localStorage
            console.error('Session invalid:', error);
            localStorage.removeItem('user');
            setUser(null);
          }
        }
      } catch (error) {
        console.error('Error checking auth:', error);
        localStorage.removeItem('user');
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await authAPI.login({ email, password });
      
      // Store access token in localStorage for Bearer auth
      if (response.access_token) {
        localStorage.setItem('access_token', response.access_token);
      }
      if (response.refresh_token) {
        localStorage.setItem('refresh_token', response.refresh_token);
      }
      
      // Fetch full user data from the backend
      try {
        const userInfo = await authAPI.getCurrentUser();
        const userData: User = {
          id: userInfo.id,
          email: userInfo.email,
          name: userInfo.name,
          created_at: userInfo.created_at,
        };
        
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
      } catch (fetchError) {
        // If we can't fetch user info, store basic data
        const userData: User = {
          id: '',
          email,
          name: '',
        };
        
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
      }
    } catch (err) {
      console.error('Login error:', err);
      const error = err as { response?: { data?: { detail?: string } } };
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  const register = async (name: string, email: string, password: string): Promise<string> => {
    try {
      const response = await authAPI.register({ name, email, password });
      
      // Store the API key to show to user
      const apiKey = response.api_key;
      
      // After successful registration, automatically log the user in
      try {
        const loginResponse = await authAPI.login({ email, password });
        
        // Store access token in localStorage for Bearer auth
        if (loginResponse.access_token) {
          localStorage.setItem('access_token', loginResponse.access_token);
        }
        if (loginResponse.refresh_token) {
          localStorage.setItem('refresh_token', loginResponse.refresh_token);
        }
        
        // Store user data with the API key
        const userData: User = {
          id: response.id,
          email: response.email,
          name: response.name,
          apiKey: apiKey,
          created_at: response.created_at,
        };
        
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
        
        return apiKey;
      } catch (loginError) {
        console.error('Auto-login after registration failed:', loginError);
        // Still return the API key even if auto-login fails
        const userData: User = {
          id: response.id,
          email: response.email,
          name: response.name,
          apiKey: apiKey,
          created_at: response.created_at,
        };
        
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
        
        return apiKey;
      }
    } catch (err) {
      console.error('Registration error:', err);
      const error = err as { response?: { data?: { detail?: string } }; message?: string };
      const errorMessage = error.response?.data?.detail || error.message || 'Registration failed';
      throw new Error(errorMessage);
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('user');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
