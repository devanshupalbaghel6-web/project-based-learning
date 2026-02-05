import apiClient from './api';

/**
 * Onboarding API Service
 */

export const onboardingService = {
  /**
   * Get initial onboarding questions
   */
  getInitialQuestions: async () => {
    const response = await apiClient.get('/onboarding/questions');
    return response.data;
  },

  /**
   * Send chat message during onboarding
   */
  sendChatMessage: async (message, conversationHistory = []) => {
    const response = await apiClient.post('/onboarding/chat', {
      message,
      conversation_history: conversationHistory,
    });
    return response.data;
  },

  /**
   * Complete onboarding process
   */
  completeOnboarding: async (onboardingData) => {
    const response = await apiClient.post('/onboarding/complete', onboardingData);
    return response.data;
  },
};

export default onboardingService;
