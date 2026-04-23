import apiClient from './api';

/**
 * Resources API Service
 */

export const resourcesService = {
  /**
   * Search for resources
   */
  searchResources: async (query, platforms = null, limit = 20) => {
    const response = await apiClient.post('/resources/search', {
      query,
      platforms,
      limit,
    });
    return response.data;
  },

  /**
   * Get recommended resources
   */
  getRecommendedResources: async () => {
    const response = await apiClient.get('/resources/recommended');
    return response.data;
  },

  /**
   * Get saved resources
   */
  getSavedResources: async (platform = null, skip = 0, limit = 20) => {
    const response = await apiClient.get('/resources/saved', {
      params: {
        platform,
        skip,
        limit,
      },
    });
    return response.data;
  },

  /**
   * Get recent resource queries
   */
  getRecentQueries: async (limit = 5) => {
    const response = await apiClient.get('/resources/recent-queries', {
      params: { limit },
    });
    return response.data;
  },

  /**
   * Save a resource
   */
  saveResource: async (resourceId) => {
    const response = await apiClient.post(`/resources/${resourceId}/save`);
    return response.data;
  },

  /**
   * Unsave a resource
   */
  unsaveResource: async (resourceId) => {
    const response = await apiClient.delete(`/resources/${resourceId}/save`);
    return response.data;
  },

  /**
   * Get resources by platform
   */
  getResourcesByPlatform: async (platform, skip = 0, limit = 20) => {
    const response = await apiClient.get(`/resources/platforms/${platform}`, {
      params: { skip, limit },
    });
    return response.data;
  },
};

export default resourcesService;
