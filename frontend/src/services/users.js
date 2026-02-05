import apiClient from './api';

/**
 * Users API Service
 */

export const usersService = {
  /**
   * Register a new user
   */
  register: async (email, password, fullName) => {
    const response = await apiClient.post('/users/register', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  },

  /**
   * Get current user profile
   */
  getCurrentUser: async () => {
    const response = await apiClient.get('/users/me');
    return response.data;
  },

  /**
   * Update user profile
   */
  updateProfile: async (updates) => {
    const response = await apiClient.put('/users/me', updates);
    return response.data;
  },

  /**
   * Get user statistics
   */
  getUserStats: async () => {
    const response = await apiClient.get('/users/stats');
    return response.data;
  },
};

export default usersService;
