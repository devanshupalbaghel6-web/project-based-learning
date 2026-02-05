import React from 'react';
import { ChatInterface, OnboardingProgress } from './components';
import { ArrowRight } from 'lucide-react';
import Button from '@components/Button';

const OnboardingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      {/* Header */}
      <div className="container-custom py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
              <span className="text-white font-bold text-xl">AL</span>
            </div>
            <h1 className="font-heading font-bold text-2xl text-secondary-900">
              AI-Learn Hub
            </h1>
          </div>
          <button className="text-sm text-secondary-600 hover:text-secondary-900">
            Skip to Dashboard <ArrowRight className="inline ml-1" size={16} />
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="container-custom py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Side - Progress */}
          <div className="lg:col-span-1">
            <OnboardingProgress />
          </div>

          {/* Right Side - Chat */}
          <div className="lg:col-span-2">
            <div className="bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl shadow-hard overflow-hidden">
              {/* Chat Header */}
              <div className="bg-white/10 backdrop-blur-sm px-6 py-4 border-b border-white/20">
                <h2 className="text-white font-heading font-semibold text-xl">
                  EduAI Chat
                </h2>
                <p className="text-white/80 text-sm mt-1">
                  Your personalized learning assistant
                </p>
              </div>

              {/* Chat Content */}
              <div className="bg-secondary-50 h-[600px] lg:h-[700px]">
                <ChatInterface />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingPage;
