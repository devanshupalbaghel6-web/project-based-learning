import React from 'react';
import Card from '@components/Card';
import { Github, Youtube, FileText, MessageSquare } from 'lucide-react';

const iconMap = {
  GitHub: Github,
  YouTube: Youtube,
  Documentation: FileText,
  Reddit: MessageSquare,
};

const ResourceCard = ({ resource }) => {
  const Icon = iconMap[resource.platform] || FileText;

  return (
    <Card hoverable>
      <div className="flex items-start gap-4">
        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
          resource.platform === 'GitHub' ? 'bg-secondary-900' :
          resource.platform === 'YouTube' ? 'bg-error-DEFAULT' :
          resource.platform === 'Documentation' ? 'bg-primary-600' :
          'bg-warning-DEFAULT'
        }`}>
          <Icon className="text-white" size={24} />
        </div>

        <div className="flex-1">
          <h3 className="font-semibold text-lg mb-1">{resource.title}</h3>
          <p className="text-secondary-600 text-sm mb-3">{resource.description}</p>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs px-2 py-1 bg-secondary-100 rounded-full text-secondary-700">
                {resource.platform}
              </span>
              <div className="flex items-center gap-1">
                <div className="w-full bg-success-light h-1.5 rounded-full">
                  <div className="w-[92%] h-full bg-success-DEFAULT rounded-full"></div>
                </div>
              </div>
            </div>
            <span className="text-sm font-semibold text-success-dark">
              {resource.relevance}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ResourceCard;
