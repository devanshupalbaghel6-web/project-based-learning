import apiClient from './api';

/**
 * Projects API Service
 */

export const projectsService = {
  /**
   * Get all projects for current user
   */
  getProjects: async (status = null, skip = 0, limit = 10) => {
    const params = { skip, limit };
    if (status) params.status = status;
    
    const response = await apiClient.get('/projects/', { params });
    return response.data;
  },

  /**
   * Get recommended projects
   */
  getRecommendedProjects: async () => {
    const response = await apiClient.get('/projects/recommended');
    return response.data;
  },

  /**
   * Get a specific project by ID
   */
  getProject: async (projectId) => {
    const response = await apiClient.get(`/projects/${projectId}`);
    return response.data;
  },

  /**
   * Generate a custom project
   */
  generateProject: async (prompt) => {
    const response = await apiClient.post('/projects/generate', null, {
      params: { prompt },
    });
    return response.data;
  },

  /**
   * Update project status or progress
   */
  updateProject: async (projectId, updates) => {
    const response = await apiClient.put(`/projects/${projectId}`, updates);
    return response.data;
  },

  /**
   * Submit a checkpoint
   */
  submitCheckpoint: async (projectId, checkpointId, screenshotUrl, notes) => {
    const response = await apiClient.post(
      `/projects/${projectId}/checkpoints/${checkpointId}/submit`,
      {
        screenshot_url: screenshotUrl,
        notes,
      }
    );
    return response.data;
  },

  /**
   * Get project roadmap
   */
  getProjectRoadmap: async (projectId) => {
    const response = await apiClient.get(`/projects/${projectId}/roadmap`);
    return response.data;
  },
};

export default projectsService;
