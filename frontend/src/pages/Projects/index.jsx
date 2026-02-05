import React, { useState } from 'react';
import { ProjectCard, ProjectTabs } from './components';
import Button from '@components/Button';
import { Plus, Filter } from 'lucide-react';

const mockProjects = [
  {
    id: 1,
    title: 'AI-Powered Sentiment Analysis App',
    description: 'Building a web app that analyzes social media comments using NLP models.',
    difficulty: 'Intermediate',
    domain: 'AI/ML',
    duration: '4 weeks',
    tech: 'Python',
    progress: 75,
  },
  {
    id: 2,
    title: 'Build a RAG-based Chatbot',
    description: 'Create a conversational AI that accesses external knowledge bases.',
    difficulty: 'Beginner',
    domain: 'AI/ML',
    duration: '3 Weeks',
    tech: 'Python',
  },
  {
    id: 3,
    title: 'Full-stack E-commerce with GraphQL',
    description: 'Develop a complete online store with a modern tech stack.',
    difficulty: 'Intermediate',
    domain: 'Web Dev',
    duration: '6 Weeks',
    tech: 'React/Node',
  },
  {
    id: 4,
    title: 'Predictive Stock Market Model',
    description: 'Use time-series forecasting to predict stock prices.',
    difficulty: 'Advanced',
    domain: 'Data Science',
    duration: '8 Weeks',
    tech: 'Python',
  },
];

const ProjectsPage = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-3xl mb-2">Projects</h1>
          <p className="text-secondary-600">
            Explore and build projects tailored to your learning journey
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="gap-2">
            <Filter size={20} />
            Filter
          </Button>
          <Button className="gap-2">
            <Plus size={20} />
            Generate New Project
          </Button>
        </div>
      </div>

      {/* Current Project */}
      <div className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6">
        <h2 className="font-heading font-semibold text-xl mb-4">Current Project</h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <h3 className="font-heading font-bold text-2xl mb-2">
              {mockProjects[0].title}
            </h3>
            <p className="text-secondary-600 mb-4">
              {mockProjects[0].description}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div>
                <p className="text-sm text-secondary-600 mb-1">Domain:</p>
                <p className="font-semibold">{mockProjects[0].domain}</p>
              </div>
              <div>
                <p className="text-sm text-secondary-600 mb-1">Duration:</p>
                <p className="font-semibold">{mockProjects[0].duration}</p>
              </div>
              <div>
                <p className="text-sm text-secondary-600 mb-1">Next Milestone:</p>
                <p className="font-semibold">Deploy Backend API</p>
              </div>
            </div>
            <Button>Resume Project</Button>
          </div>
          <div className="flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl font-bold text-primary-600 mb-2">
                {mockProjects[0].progress}%
              </div>
              <p className="text-secondary-600">Complete</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recommended Projects */}
      <ProjectTabs>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mockProjects.slice(1).map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      </ProjectTabs>
    </div>
  );
};

export default ProjectsPage;
