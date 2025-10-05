import axios from 'axios';
import { UserCreate, UserLogin, UserResponse, TokenResponse, AuthError } from '@/types/auth';
import { Project, ProjectCreate, ProjectUpdate, ContributorAdd } from '@/types/project';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for cookies
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token if available
api.interceptors.request.use(
  (config) => {
    // Add Bearer token from localStorage if available
    if (typeof window !== 'undefined') {
      const userData = localStorage.getItem('user');
      if (userData) {
        try {
          const user = JSON.parse(userData);
          const accessToken = localStorage.getItem('access_token');
          if (accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`;
          }
        } catch (error) {
          console.error('Error parsing user data:', error);
        }
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If 401 and we haven't retried yet, try to refresh the token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const refreshResponse = await api.post('/auth/refresh');
        
        // Store new tokens
        if (refreshResponse.data.access_token) {
          localStorage.setItem('access_token', refreshResponse.data.access_token);
        }
        if (refreshResponse.data.refresh_token) {
          localStorage.setItem('refresh_token', refreshResponse.data.refresh_token);
        }
        
        // Update Authorization header with new token
        originalRequest.headers.Authorization = `Bearer ${refreshResponse.data.access_token}`;
        
        // Retry the original request
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, redirect to login
        if (typeof window !== 'undefined') {
          localStorage.removeItem('user');
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    
    return Promise.reject(error);
  }
);

export const authAPI = {
  // Register a new user - POST /api/v1/auth/register
  register: async (userData: UserCreate): Promise<UserResponse> => {
    const response = await api.post<UserResponse>('/auth/register', userData);
    return response.data;
  },

  // Login user - POST /api/v1/auth/login
  login: async (credentials: UserLogin): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/auth/login', credentials);
    return response.data;
  },

  // Logout user - POST /api/v1/auth/logout
  logout: async (): Promise<void> => {
    await api.post('/auth/logout');
  },

  // Get current user - GET /api/v1/auth/me
  getCurrentUser: async (): Promise<UserResponse> => {
    const response = await api.get<UserResponse>('/auth/me');
    return response.data;
  },

  // Refresh token - POST /api/v1/auth/refresh
  refreshToken: async (): Promise<TokenResponse> => {
    const response = await api.post<TokenResponse>('/auth/refresh');
    return response.data;
  },

  // Rotate API key - POST /api/v1/auth/api-key/rotate
  rotateApiKey: async (): Promise<UserResponse> => {
    const response = await api.post<UserResponse>('/auth/api-key/rotate');
    return response.data;
  },
};

export const projectAPI = {
  // Get all projects - GET /api/v1/projects
  getProjects: async (): Promise<Project[]> => {
    const response = await api.get<Project[]>('/projects');
    return response.data;
  },

  // Get project by ID - GET /api/v1/projects/:id
  getProject: async (projectId: string): Promise<Project> => {
    const response = await api.get<Project>(`/projects/${projectId}`);
    return response.data;
  },

  // Create project - POST /api/v1/projects
  createProject: async (project: ProjectCreate): Promise<Project> => {
    const response = await api.post<Project>('/projects', project);
    return response.data;
  },

  // Update project - PUT /api/v1/projects/:id
  updateProject: async (projectId: string, updates: ProjectUpdate): Promise<Project> => {
    const response = await api.put<Project>(`/projects/${projectId}`, updates);
    return response.data;
  },

  // Delete project - DELETE /api/v1/projects/:id
  deleteProject: async (projectId: string): Promise<void> => {
    await api.delete(`/projects/${projectId}`);
  },

  // Add contributor - POST /api/v1/projects/:id/contributors
  addContributor: async (projectId: string, contributor: ContributorAdd): Promise<any> => {
    const response = await api.post(`/projects/${projectId}/contributors`, contributor);
    return response.data;
  },

  // Remove contributor - DELETE /api/v1/projects/:id/contributors/:userId
  removeContributor: async (projectId: string, userId: string): Promise<any> => {
    const response = await api.delete(`/projects/${projectId}/contributors/${userId}`);
    return response.data;
  },
};

export default api;
