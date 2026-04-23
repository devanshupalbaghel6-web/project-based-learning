import React from 'react';

const tabItems = [
  { key: 'all', label: 'All Projects' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'completed', label: 'Completed' },
  { key: 'recommended', label: 'Recommended' },
];

const ProjectTabs = ({ activeTab = 'all', onTabChange, children }) => {
  return (
    <div className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="font-heading font-semibold text-2xl">Projects</h2>
      </div>

      <div className="flex gap-2 mb-6 border-b border-secondary-200">
        {tabItems.map((tab) => (
          <button
            key={tab.key}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === tab.key
                ? 'text-primary-600 border-primary-600'
                : 'text-secondary-600 border-transparent hover:text-secondary-900'
            }`}
            onClick={() => onTabChange?.(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {children}
    </div>
  );
};

export default ProjectTabs;
