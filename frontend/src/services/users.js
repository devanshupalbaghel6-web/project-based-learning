import apiClient from './api';

/**
 * Users API Service
 */

export const usersService = {
  /**
   * Register a new user
   */
  register: async (email, password, fullName) => {
    const response = await apiClient.post('/auth/register', {
      email,
      password,
      name: fullName,
    });
    return response.data;
  },

  /**
   * Get current user profile
   */
  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  /**
   * Update user profile
   */
  updateProfile: async (updates) => {
    const response = await apiClient.put('/auth/me', updates);
    return response.data;
  },

  /**
   * Get user statistics
   */
  getUserStats: async () => {
    const response = await apiClient.get('/progress/stats');
    return response.data;
  },
};

export default usersService;
