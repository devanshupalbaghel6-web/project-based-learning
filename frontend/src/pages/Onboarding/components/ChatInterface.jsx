import React, { useState } from 'react';
import { Send, Bot } from 'lucide-react';
import Button from '@components/Button';
import Spinner from '@components/Spinner';
import onboardingService from '@services/onboarding';

const ChatMessage = ({ message, isBot }) => (
  <div className={`flex gap-3 ${isBot ? '' : 'flex-row-reverse'}`}>
    <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
      isBot ? 'bg-primary-100' : 'bg-secondary-200'
    }`}>
      {isBot ? (
        <Bot size={20} className="text-primary-600" />
      ) : (
        <span className="text-secondary-700 font-semibold text-sm">You</span>
      )}
    </div>
    <div className={`flex-1 ${isBot ? 'pr-12' : 'pl-12'}`}>
      <div className={`rounded-2xl px-4 py-3 ${
        isBot 
          ? 'bg-white border border-secondary-200' 
          : 'bg-primary-600 text-white'
      }`}>
        <p className="text-sm leading-relaxed">{message}</p>
      </div>
    </div>
  </div>
);

const QuickAction = ({ children, onClick }) => (
  <button
    onClick={onClick}
    className="px-4 py-2 bg-white border-2 border-secondary-300 rounded-full text-sm font-medium text-secondary-700 hover:border-primary-500 hover:text-primary-600 transition-all duration-200"
  >
    {children}
  </button>
);

const ChatInterface = ({ onComplete, onProgressChange }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hi there! Let's personalize your learning path. What is your main goal right now?",
      isBot: true,
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const quickActions = [
    'Learn a new skill',
    'Build a portfolio project',
    'Upskill for my job',
    'Explore a new field',
  ];

  const completeOnboardingIfPossible = async (result) => {
    if (!result?.is_complete) {
      return;
    }

    const extracted = result?.extracted_info || {};
    await onboardingService.completeOnboarding({
      experience_level: extracted.experience_level || 'beginner',
      interests: extracted.interests || [],
      current_skills: extracted.current_skills || [],
      primary_goal: extracted.primary_goal || 'learn',
      time_commitment: extracted.time_commitment || '5-7 hours/week',
      preferred_learning_style: extracted.preferred_learning_style || 'hands_on',
    });

    if (onComplete) {
      onComplete();
    }
  };

  const sendMessage = async (text) => {
    const trimmed = text.trim();
    if (!trimmed || isLoading) {
      return;
    }

    setError('');
    const userMessage = {
      id: Date.now(),
      text: trimmed,
      isBot: false,
    };

    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await onboardingService.sendChatMessage(
        trimmed,
        nextMessages.map((item) => ({
          role: item.isBot ? 'assistant' : 'user',
          content: item.text,
        }))
      );

      const botText = response?.message || 'Thanks! Can you share a bit more detail?';

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text: botText,
          isBot: true,
        },
      ]);

      await completeOnboardingIfPossible(response);
      const totalMessages = nextMessages.length + 1;
      const step = Math.min(4, Math.max(1, Math.floor(totalMessages / 2) + 1));
      onProgressChange?.(step);
    } catch (sendError) {
      setError(sendError?.response?.data?.detail || 'Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = () => sendMessage(inputValue);

  const handleQuickAction = (action) => {
    sendMessage(action);
  };

  React.useEffect(() => {
    onProgressChange?.(1);
  }, [onProgressChange]);

  React.useEffect(() => {
    let mounted = true;
    const hydrateInitialQuestion = async () => {
      try {
        const payload = await onboardingService.getInitialQuestions();
        const question = payload?.questions?.[0]?.question;
        if (!mounted || !question) return;
        setMessages((prev) =>
          prev.length === 1 && prev[0]?.isBot
            ? [{ ...prev[0], text: question }]
            : prev
        );
      } catch {
        // Keep local fallback greeting if endpoint is unavailable.
      }
    };
    hydrateInitialQuestion();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="flex flex-col h-full">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message.text}
            isBot={message.isBot}
          />
        ))}
        {isLoading && (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
              <Bot size={20} className="text-primary-600" />
            </div>
            <div className="bg-white border border-secondary-200 rounded-2xl px-4 py-3">
              <Spinner size="sm" />
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="px-6 pb-4">
        <div className="flex flex-wrap gap-2">
          {quickActions.map((action) => (
            <QuickAction key={action} onClick={() => handleQuickAction(action)}>
              {action}
            </QuickAction>
          ))}
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-secondary-200 p-6">
        {error && <p className="text-sm text-error-DEFAULT mb-3">{error}</p>}
        <div className="flex gap-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your response..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <Button onClick={handleSend} className="px-6" disabled={isLoading}>
            <Send size={20} />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
