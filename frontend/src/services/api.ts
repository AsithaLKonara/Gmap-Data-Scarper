import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config: any) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error: any) => {
        return Promise.reject(error);
    }
);

export interface DiscoveryRequest {
    platforms: string[];
    skills: string[];
    cities: string[];
    providers: string[];
    collection_name?: string;
}

export const socialDiscoveryApi = {
    startDiscovery: async (data: DiscoveryRequest) => {
        const response = await api.post('/api/social-scraper/discovery/undergraduates', data);
        return response.data;
    },
    getDiscoveryStatus: async (collectionId: number) => {
        const response = await api.get(`/api/social-scraper/discovery/status/${collectionId}`);
        return response.data;
    }
};

export default api;
