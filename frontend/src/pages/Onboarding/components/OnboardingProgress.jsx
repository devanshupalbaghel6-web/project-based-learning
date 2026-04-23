import React from 'react';
import { CheckCircle2, Circle } from 'lucide-react';

const steps = [
  { id: 1, name: 'Goal Setting' },
  { id: 2, name: 'Experience Level' },
  { id: 3, name: 'Interests' },
  { id: 4, name: 'Project Generation' },
];

const OnboardingProgress = ({ currentStep = 1 }) => {
  return (
    <div className="bg-white rounded-2xl shadow-soft p-6 border border-secondary-200">
      <h3 className="font-heading font-semibold text-lg mb-6">Onboarding Progress</h3>
      
      <div className="space-y-4">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center gap-3">
            <div className="relative">
              {step.id < currentStep ? (
                <CheckCircle2 className="text-success-DEFAULT" size={24} />
              ) : step.id === currentStep ? (
                <div className="w-6 h-6 rounded-full bg-primary-600 border-4 border-primary-200"></div>
              ) : (
                <Circle className="text-secondary-300" size={24} />
              )}
              {index < steps.length - 1 && (
                <div className={`absolute left-3 top-6 w-0.5 h-8 ${
                  step.id < currentStep ? 'bg-success-DEFAULT' : 'bg-secondary-200'
                }`}></div>
              )}
            </div>
            <span className={`text-sm font-medium ${
              step.id < currentStep
                ? 'text-success-dark' 
                : step.id === currentStep
                ? 'text-primary-600' 
                : 'text-secondary-400'
            }`}>
              {step.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OnboardingProgress;
