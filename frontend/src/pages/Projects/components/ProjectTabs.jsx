import React from 'react';

const ProjectTabs = ({ children }) => {
  return (
    <div className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="font-heading font-semibold text-2xl">Projects</h2>
      </div>

      <div className="flex gap-2 mb-6 border-b border-secondary-200">
        <button className="px-4 py-2 font-medium text-primary-600 border-b-2 border-primary-600">
          All Projects
        </button>
        <button className="px-4 py-2 font-medium text-secondary-600 hover:text-secondary-900">
          In Progress
        </button>
        <button className="px-4 py-2 font-medium text-secondary-600 hover:text-secondary-900">
          Completed
        </button>
        <button className="px-4 py-2 font-medium text-secondary-600 hover:text-secondary-900">
          Recommended
        </button>
      </div>

      {children}
    </div>
  );
};

export default ProjectTabs;
