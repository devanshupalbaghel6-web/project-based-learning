import apiClient from './api';

/**
 * Progress API Service
 */
export const progressService = {
  getRoadmap: async (roadmapId) => {
    const response = await apiClient.get(`/progress/roadmap/${roadmapId}`);
    return response.data;
  },

  getProgress: async (roadmapId) => {
    const response = await apiClient.get(`/progress/progress/${roadmapId}`);
    return response.data;
  },

  getStats: async () => {
    const response = await apiClient.get('/progress/stats');
    return response.data;
  },

  getRecentActivity: async (days = 7) => {
    const response = await apiClient.get('/progress/activity/recent', {
      params: { days },
    });
    return response.data;
  },

  completeCheckpoint: async (checkpointId) => {
    const response = await apiClient.post(`/progress/checkpoints/${checkpointId}/complete`);
    return response.data;
  },
};

export default progressService;
