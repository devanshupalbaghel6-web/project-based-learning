import React from 'react';
import { Search } from 'lucide-react';
import Input from '@components/Input';

const ResourceFilters = () => {
  const platforms = [
    'All Resources',
    'GitHub Repos',
    'YouTube Tutorials',
    'Documentation',
    'Reddit Discussions',
    'Research Papers',
    'Blogs',
  ];

  return (
    <div className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6">
      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-400" size={20} />
          <input
            type="text"
            placeholder="Search resources or enter a topic..."
            className="w-full pl-12 pr-4 py-3 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
      </div>

      {/* Platform Filters */}
      <div>
        <h3 className="font-semibold text-sm text-secondary-700 mb-3">Filter by Platform</h3>
        <div className="flex flex-wrap gap-2">
          {platforms.map((platform, index) => (
            <button
              key={platform}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                index === 0
                  ? 'bg-primary-600 text-white'
                  : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
              }`}
            >
              {platform}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResourceFilters;
