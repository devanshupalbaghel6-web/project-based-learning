import React, { useState } from 'react';
import { Send, Bot } from 'lucide-react';
import Button from '@components/Button';
import Card from '@components/Card';

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

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hi there! To curate your personalized learning journey, let's start with your goals. What is your primary goal for this month?",
      isBot: true,
    },
  ]);
  const [inputValue, setInputValue] = useState('');

  const quickActions = [
    'Learn a new skill',
    'Build a portfolio project',
    'Upskill for my job',
    'Explore a new field',
  ];

  const handleSend = () => {
    if (!inputValue.trim()) return;

    setMessages([
      ...messages,
      {
        id: messages.length + 1,
        text: inputValue,
        isBot: false,
      },
    ]);
    setInputValue('');
  };

  const handleQuickAction = (action) => {
    setMessages([
      ...messages,
      {
        id: messages.length + 1,
        text: action,
        isBot: false,
      },
    ]);
  };

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
        <div className="flex gap-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your response..."
            className="flex-1 px-4 py-3 border border-secondary-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
          <Button onClick={handleSend} className="px-6">
            <Send size={20} />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
