import { defineStore } from 'pinia';
import api from '@/api';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        isAuthenticated: false,
        authError: null,
        isAuthChecked: false, // New state
    }),
    actions: {
        async login(credentials) {
            this.authError = null;
            try {
                const response = await api.post('/auth/login', credentials);
                this.user = response.data;
                this.isAuthenticated = true;
                return true;
            } catch (error) {
                this.authError = error.response?.data?.detail || 'Login failed';
                this.isAuthenticated = false;
                throw error;
            }
        },
        async signup(userInfo) {
            this.authError = null;
            try {
                await api.post('/auth/signup', userInfo);
                return true;
            } catch (error) {
                this.authError = error.response?.data?.detail || 'Signup failed';
                throw error;
            }
        },
        async logout() {
            try {
                await api.post('/auth/logout');
            } catch (error) {
                console.error('Logout error', error);
            }
        },
        async checkAuth() {
            // Avoid redundant calls if already checked, unless force parameter added later
            // But router guard might call it.
            try {
                const response = await api.get('/auth/me');
                this.user = response.data;
                this.isAuthenticated = true;
            } catch (error) {
                this.user = null;
                this.isAuthenticated = false;
            } finally {
                this.isAuthChecked = true;
            }
        }
    },
});
