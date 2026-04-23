import React from 'react';
import Card from '@components/Card';
import Badge from '@components/Badge';
import Button from '@components/Button';
import ProgressBar from '@components/ProgressBar';
import { Clock, Code } from 'lucide-react';

const ProjectCard = ({ project, onAction }) => {
  const difficulty = String(project.difficulty || 'intermediate');
  const difficultyLabel = `${difficulty.charAt(0).toUpperCase()}${difficulty.slice(1)}`;
  const duration = project.estimated_duration || (project.duration_weeks ? `${project.duration_weeks} weeks` : 'Flexible');
  const tech = project.tech || project.tech_stack?.[0] || 'Multiple';
  const progressValue =
    project.progress !== undefined
      ? Number(project.progress)
      : Number(project.progress_percentage || 0);

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
        <Badge variant={difficulty === 'beginner' ? 'success' : difficulty === 'intermediate' ? 'warning' : 'error'}>
          {difficultyLabel}
        </Badge>
        <Badge variant="primary">{project.domain || 'general'}</Badge>
      </div>

      {/* Meta Info */}
      <div className="flex items-center gap-4 text-sm text-secondary-600 mb-4">
        <div className="flex items-center gap-1">
          <Clock size={16} />
          <span>{duration}</span>
        </div>
        <div className="flex items-center gap-1">
          <Code size={16} />
          <span>{tech}</span>
        </div>
      </div>

      {/* Progress */}
      {Number.isFinite(progressValue) && (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-secondary-700">Progress</span>
            <span className="text-sm font-semibold text-primary-600">{Math.round(progressValue)}%</span>
          </div>
          <ProgressBar value={Math.round(progressValue)} />
        </div>
      )}

      {/* Action Button */}
      <div className="mt-auto pt-4">
        <Button 
          variant={project.status === 'in_progress' ? 'primary' : 'outline'}
          className="w-full"
          onClick={() => onAction?.(project)}
        >
          {project.status === 'in_progress' ? 'Resume Project' : 'Start Project'}
        </Button>
      </div>
    </Card>
  );
};

export default ProjectCard;
