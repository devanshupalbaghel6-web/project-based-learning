import React, { useEffect, useState } from 'react';
import Spinner from '@components/Spinner';
import Button from '@components/Button';
import projectsService from '@services/projects';

const RoadmapsPage = () => {
  const [projects, setProjects] = useState([]);
  const [selectedRoadmap, setSelectedRoadmap] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      setError('');
      try {
        const data = await projectsService.getProjects(null, 0, 50);
        setProjects(Array.isArray(data) ? data : []);
      } catch {
        setError('Unable to load roadmap projects right now.');
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  const loadRoadmap = async (projectId) => {
    setError('');
    try {
      const roadmap = await projectsService.getProjectRoadmap(projectId);
      setSelectedRoadmap(roadmap);
    } catch {
      setError('Roadmap is not available for this project yet.');
      setSelectedRoadmap(null);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[40vh] flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-heading font-bold text-3xl mb-2">Roadmaps</h1>
        <p className="text-secondary-600">Open a project roadmap and track milestones/checkpoints.</p>
      </div>

      {error && <p className="text-sm text-error-DEFAULT">{error}</p>}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-1 bg-white rounded-xl border border-secondary-200 p-4">
          <h2 className="text-lg font-semibold mb-3">Projects</h2>
          <div className="space-y-2 max-h-[60vh] overflow-y-auto">
            {projects.map((project) => (
              <button
                key={project._id || project.id}
                onClick={() => loadRoadmap(project._id || project.id)}
                className="w-full text-left p-3 rounded-lg border border-secondary-200 hover:border-primary-400 hover:bg-primary-50 transition-colors"
              >
                <p className="font-medium">{project.title}</p>
                <p className="text-xs text-secondary-500 mt-1">{project.status}</p>
              </button>
            ))}
            {projects.length === 0 && <p className="text-sm text-secondary-500">No projects yet.</p>}
          </div>
        </div>

        <div className="xl:col-span-2 bg-white rounded-xl border border-secondary-200 p-4">
          {!selectedRoadmap ? (
            <p className="text-secondary-500">Select a project to load its roadmap.</p>
          ) : (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">{selectedRoadmap.title || 'Project Roadmap'}</h2>
              {(selectedRoadmap.milestones || []).map((milestone) => (
                <div key={milestone._id} className="p-3 border border-secondary-200 rounded-lg">
                  <p className="font-medium">{milestone.title}</p>
                  <p className="text-sm text-secondary-600 mt-1">{milestone.description}</p>
                  <div className="mt-2 space-y-1">
                    {(milestone.checkpoints || []).map((checkpoint) => (
                      <p key={checkpoint._id} className="text-sm text-secondary-700">
                        - {checkpoint.title}
                      </p>
                    ))}
                  </div>
                </div>
              ))}
              {(!selectedRoadmap.milestones || selectedRoadmap.milestones.length === 0) && (
                <p className="text-sm text-secondary-500">No milestones yet for this roadmap.</p>
              )}
              <Button variant="outline" onClick={() => setSelectedRoadmap(null)}>
                Close Roadmap
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RoadmapsPage;

