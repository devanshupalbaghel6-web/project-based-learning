import React from 'react';
import Card from '@components/Card';
import Badge from '@components/Badge';
import Button from '@components/Button';
import ProgressBar from '@components/ProgressBar';
import { Clock, Code, TrendingUp } from 'lucide-react';

const ProjectCard = ({ project }) => {
  return (
    <Card hoverable className="h-full flex flex-col">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="font-heading font-semibold text-xl mb-2">
            {project.title}
          </h3>
          <p className="text-secondary-600 text-sm mb-3">
            {project.description}
          </p>
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-2 mb-4">
        <Badge variant={project.difficulty === 'Beginner' ? 'success' : project.difficulty === 'Intermediate' ? 'warning' : 'error'}>
          {project.difficulty}
        </Badge>
        <Badge variant="primary">{project.domain}</Badge>
      </div>

      {/* Meta Info */}
      <div className="flex items-center gap-4 text-sm text-secondary-600 mb-4">
        <div className="flex items-center gap-1">
          <Clock size={16} />
          <span>{project.duration}</span>
        </div>
        <div className="flex items-center gap-1">
          <Code size={16} />
          <span>{project.tech}</span>
        </div>
      </div>

      {/* Progress */}
      {project.progress !== undefined && (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-secondary-700">Progress</span>
            <span className="text-sm font-semibold text-primary-600">{project.progress}%</span>
          </div>
          <ProgressBar value={project.progress} />
        </div>
      )}

      {/* Action Button */}
      <div className="mt-auto pt-4">
        <Button 
          variant={project.progress !== undefined ? "primary" : "outline"} 
          className="w-full"
        >
          {project.progress !== undefined ? 'Resume Project' : 'Start Project'}
        </Button>
      </div>
    </Card>
  );
};

export default ProjectCard;
