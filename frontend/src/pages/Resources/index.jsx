import React from 'react';
import { ResourceCard, ResourceFilters } from './components';

const mockResources = [
  {
    id: 1,
    title: 'TensorFlow 2.0 for Deep Learning Projects',
    description: 'Comprehensive guide with practical examples and code blocks for building deep learning models.',
    platform: 'GitHub',
    relevance: '95%',
  },
  {
    id: 2,
    title: 'Intro to Reinforcement Learning',
    description: 'A 30-minute video covering core concepts and real-world applications.',
    platform: 'YouTube',
    relevance: '88%',
  },
  {
    id: 3,
    title: 'PyTorch Official Docs: Tensors',
    description: 'Reference for manipulating multi-dimensional arrays, essential for neural networks.',
    platform: 'Documentation',
    relevance: '92%',
  },
];

const ResourcesPage = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="font-heading font-bold text-3xl mb-2">Resources</h1>
        <p className="text-secondary-600">
          Curated learning materials from across the web
        </p>
      </div>

      {/* Filters */}
      <ResourceFilters />

      {/* Resources Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="font-heading font-semibold text-xl">
            Recommended for You
          </h2>
          <button className="text-primary-600 hover:text-primary-700 font-medium text-sm">
            View All
          </button>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {mockResources.map((resource) => (
            <ResourceCard key={resource.id} resource={resource} />
          ))}
        </div>
      </div>

      {/* Recent Queries */}
      <div className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6">
        <h2 className="font-heading font-semibold text-xl mb-4">Recent Queries</h2>
        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 hover:bg-secondary-50 rounded-lg cursor-pointer transition-colors">
            <span className="text-secondary-700">Quantum Computing Basics</span>
            <span className="text-xs text-secondary-500">2 hours ago</span>
          </div>
          <div className="flex items-center justify-between p-3 hover:bg-secondary-50 rounded-lg cursor-pointer transition-colors">
            <span className="text-secondary-700">Flask API Development</span>
            <span className="text-xs text-secondary-500">1 day ago</span>
          </div>
          <div className="flex items-center justify-between p-3 hover:bg-secondary-50 rounded-lg cursor-pointer transition-colors">
            <span className="text-secondary-700">Data Science Roadmap 2024</span>
            <span className="text-xs text-secondary-500">3 days ago</span>
          </div>
        </div>
      </div>

      {/* Saved for Later */}
      <div className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6">
        <h2 className="font-heading font-semibold text-xl mb-4">Saved for Later</h2>
        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 hover:bg-secondary-50 rounded-lg cursor-pointer transition-colors">
            <span className="text-secondary-700">Generative AI on AWS (YouTube)</span>
          </div>
          <div className="flex items-center justify-between p-3 hover:bg-secondary-50 rounded-lg cursor-pointer transition-colors">
            <span className="text-secondary-700">Awesome-AI-Tools (GitHub)</span>
          </div>
          <div className="flex items-center justify-between p-3 hover:bg-secondary-50 rounded-lg cursor-pointer transition-colors">
            <span className="text-secondary-700">Understanding Transformers (Blog Post)</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResourcesPage;
