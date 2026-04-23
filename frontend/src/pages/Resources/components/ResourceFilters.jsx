import React from 'react';
import { Search } from 'lucide-react';

const ResourceFilters = ({
  searchValue,
  onSearchValueChange,
  onSearchSubmit,
  selectedPlatform,
  onSelectPlatform,
  isLoading,
}) => {
  const platforms = [
    { label: 'All Resources', value: 'all' },
    { label: 'GitHub Repos', value: 'github' },
    { label: 'YouTube Tutorials', value: 'youtube' },
    { label: 'Documentation', value: 'documentation' },
    { label: 'Reddit Discussions', value: 'reddit' },
    { label: 'StackOverflow', value: 'stackoverflow' },
    { label: 'Google', value: 'google' },
  ];

  return (
    <div className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6">
      {/* Search */}
      <div className="mb-6">
        <form className="relative" onSubmit={onSearchSubmit}>
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-secondary-400" size={20} />
          <input
            type="text"
            value={searchValue}
            onChange={(event) => onSearchValueChange?.(event.target.value)}
            placeholder="Search resources or enter a topic..."
            className="w-full pl-12 pr-4 py-3 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            disabled={isLoading}
          />
        </form>
      </div>

      {/* Platform Filters */}
      <div>
        <h3 className="font-semibold text-sm text-secondary-700 mb-3">Filter by Platform</h3>
        <div className="flex gap-2 overflow-x-auto pb-1">
          {platforms.map((platform) => (
            <button
              key={platform.value}
              type="button"
              onClick={() => onSelectPlatform?.(platform.value)}
              disabled={isLoading}
              className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                selectedPlatform === platform.value
                  ? 'bg-primary-600 text-white'
                  : 'bg-secondary-100 text-secondary-700 hover:bg-secondary-200'
              }`}
            >
              {platform.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResourceFilters;
