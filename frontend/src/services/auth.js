import apiClient from './api';

/**
 * Authentication API Service
 */
export const authService = {
  register: async ({ email, password, name }) => {
    const response = await apiClient.post('/auth/register', {
      email,
      password,
      name,
    });
    return response.data;
  },

  login: async ({ email, password }) => {
    const response = await apiClient.post('/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  updateCurrentUser: async (payload) => {
    const response = await apiClient.put('/auth/me', payload);
    return response.data;
  },

  changePassword: async ({ oldPassword, newPassword }) => {
    const response = await apiClient.post('/auth/change-password', null, {
      params: {
        old_password: oldPassword,
        new_password: newPassword,
      },
    });
    return response.data;
  },
};

export default authService;
