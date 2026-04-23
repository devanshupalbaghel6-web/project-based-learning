import React from 'react';
import Card from '@components/Card';
import { Github, Youtube, FileText, MessageSquare } from 'lucide-react';

const iconMap = {
  github: Github,
  youtube: Youtube,
  documentation: FileText,
  reddit: MessageSquare,
  stackoverflow: MessageSquare,
  google: FileText,
};

const ResourceCard = ({ resource, onToggleSave, isSaving }) => {
  const platform = String(resource.platform || resource.source || 'other').toLowerCase();
  const platformLabel = platform.charAt(0).toUpperCase() + platform.slice(1);
  const Icon = iconMap[platform] || FileText;
  const relevance = Math.round(Number(resource.relevance_score || 0) * 100) || Math.round(Number(resource.score || 0));

  return (
    <Card hoverable>
      <div className="flex items-start gap-4">
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
          platform === 'github' ? 'bg-secondary-900' :
          platform === 'youtube' ? 'bg-error-DEFAULT' :
          platform === 'documentation' ? 'bg-primary-600' :
          'bg-warning-DEFAULT'
        }`}>
          <Icon className="text-white" size={24} />
        </div>

        <div className="flex-1">
          <h3 className="font-semibold text-lg mb-1">
            <a href={resource.url} target="_blank" rel="noreferrer" className="hover:text-primary-600">
              {resource.title}
            </a>
          </h3>
          <p className="text-secondary-600 text-sm mb-3">{resource.description}</p>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs px-2 py-1 bg-secondary-100 rounded-full text-secondary-700">
                {platformLabel}
              </span>
              <div className="w-16 bg-success-light h-1.5 rounded-full">
                <div
                  className="h-full bg-success-DEFAULT rounded-full"
                  style={{ width: `${Math.min(Math.max(relevance, 0), 100)}%` }}
                ></div>
                </div>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-sm font-semibold text-success-dark">{relevance}%</span>
              {onToggleSave && (
                <button
                  type="button"
                  className="text-xs px-3 py-1 rounded-md border border-secondary-300 hover:border-primary-500"
                  onClick={() => onToggleSave(resource)}
                  disabled={isSaving}
                >
                  {resource.saved ? 'Saved' : 'Save'}
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ResourceCard;
