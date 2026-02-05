import React from 'react';
import { DashboardStats, RecentActivity } from './components';
import Card from '@components/Card';
import Button from '@components/Button';
import { Calendar, ArrowRight } from 'lucide-react';

const DashboardPage = () => {
  const upcomingDeadlines = [
    { id: 1, title: 'RAG Chatbot Prototype Due', date: 'Oct 15' },
    { id: 2, title: 'E-commerce Backend Review', date: 'Oct 22' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="font-heading font-bold text-3xl mb-2">
          Welcome back, Alex! 👋
        </h1>
        <p className="text-secondary-600">
          Here's what's happening with your learning journey today
        </p>
      </div>

      {/* Stats */}
      <DashboardStats />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Current Project */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <h2 className="font-heading font-semibold text-2xl mb-4">
              Continue Learning
            </h2>
            <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl p-6 border border-primary-200">
              <h3 className="font-heading font-bold text-xl mb-2">
                AI-Powered Sentiment Analysis App
              </h3>
              <p className="text-secondary-700 mb-4">
                Building a web app that analyzes social media comments using NLP models
              </p>
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-medium">Overall Progress</span>
                <span className="text-sm font-bold text-primary-600">75%</span>
              </div>
              <div className="w-full bg-white rounded-full h-3 mb-4">
                <div className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full" style={{ width: '75%' }}></div>
              </div>
              <div className="flex gap-3">
                <Button>Continue Project</Button>
                <Button variant="outline">View Roadmap</Button>
              </div>
            </div>
          </Card>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card hoverable className="cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-lg mb-1">Explore Projects</h3>
                  <p className="text-sm text-secondary-600">Find your next challenge</p>
                </div>
                <ArrowRight className="text-primary-600" size={24} />
              </div>
            </Card>
            <Card hoverable className="cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-lg mb-1">Browse Resources</h3>
                  <p className="text-sm text-secondary-600">Curated learning materials</p>
                </div>
                <ArrowRight className="text-primary-600" size={24} />
              </div>
            </Card>
          </div>
        </div>

        {/* Right Column - Sidebar Content */}
        <div className="space-y-6">
          {/* Upcoming Deadlines */}
          <Card>
            <div className="flex items-center gap-2 mb-4">
              <Calendar className="text-primary-600" size={20} />
              <h3 className="font-heading font-semibold text-lg">Quick Actions</h3>
            </div>
            <div className="space-y-3">
              {upcomingDeadlines.map((deadline) => (
                <div key={deadline.id} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                  <div className="flex-1">
                    <p className="font-medium text-sm">{deadline.title}</p>
                  </div>
                  <span className="text-xs font-semibold text-primary-600 bg-primary-100 px-2 py-1 rounded">
                    {deadline.date}
                  </span>
                </div>
              ))}
            </div>
          </Card>

          {/* Recent Activity */}
          <RecentActivity />
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
