import React, { useEffect, useMemo, useState } from 'react';
import { ProjectCard, ProjectTabs } from './components';
import Button from '@components/Button';
import Spinner from '@components/Spinner';
import { Plus, Filter } from 'lucide-react';
import projectsService from '@services/projects';

const ProjectsPage = () => {
  const [projects, setProjects] = useState([]);
  const [activeTab, setActiveTab] = useState('all');
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');

  const loadProjects = async () => {
    setIsLoading(true);
    setError('');

    try {
      const projectData = await projectsService.getProjects(null, 0, 50);
      setProjects(Array.isArray(projectData) ? projectData : []);
    } catch (loadError) {
      setError('Failed to load projects.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  const recommendedProjects = useMemo(
    () => projects.filter((item) => item.status === 'not_started' || item.source === 'ai_generated'),
    [projects]
  );

  const filteredProjects = useMemo(() => {
    if (activeTab === 'all') return projects;
    if (activeTab === 'recommended') return recommendedProjects;
    return projects.filter((item) => item.status === activeTab);
  }, [activeTab, projects, recommendedProjects]);

  const currentProject = useMemo(
    () => projects.find((item) => item.status === 'in_progress') || projects[0] || null,
    [projects]
  );

  const handleGenerateCustomProject = async () => {
    const prompt = window.prompt('Describe the custom project you want to generate:');
    if (!prompt) {
      return;
    }

    setIsGenerating(true);
    setError('');

    try {
      await projectsService.generateProject(prompt);
      await loadProjects();
    } catch (generateError) {
      setError('Failed to generate a project right now.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateRecommendations = async () => {
    setIsGenerating(true);
    setError('');

    try {
      await projectsService.getRecommendedProjects();
      await loadProjects();
      setActiveTab('recommended');
    } catch (recommendError) {
      setError('Unable to generate recommendations right now.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleProjectAction = async (project) => {
    if (project.status !== 'in_progress') {
      try {
        await projectsService.updateProject(project._id || project.id, { status: 'in_progress' });
        await loadProjects();
      } catch {
        setError('Unable to update project status.');
      }
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-3xl mb-2">Projects</h1>
          <p className="text-secondary-600">
            Explore and build projects tailored to your learning journey
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="outline" className="gap-2">
            <Filter size={20} />
            Filter
          </Button>
          <Button className="gap-2" onClick={handleGenerateCustomProject} disabled={isGenerating}>
            <Plus size={20} />
            {isGenerating ? 'Generating...' : 'Generate New Project'}
          </Button>
        </div>
      </div>

      {error && <p className="text-sm text-error-DEFAULT">{error}</p>}

      {/* Current Project */}
      <div className="bg-white rounded-xl shadow-soft border border-secondary-200 p-6">
        <h2 className="font-heading font-semibold text-xl mb-4">Current Project</h2>
        {currentProject ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <h3 className="font-heading font-bold text-2xl mb-2">{currentProject.title}</h3>
              <p className="text-secondary-600 mb-4">{currentProject.description}</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div>
                  <p className="text-sm text-secondary-600 mb-1">Domain:</p>
                  <p className="font-semibold">{currentProject.domain || 'general'}</p>
                </div>
                <div>
                  <p className="text-sm text-secondary-600 mb-1">Duration:</p>
                  <p className="font-semibold">{currentProject.estimated_duration || 'Flexible'}</p>
                </div>
                <div>
                  <p className="text-sm text-secondary-600 mb-1">Status:</p>
                  <p className="font-semibold">{currentProject.status}</p>
                </div>
              </div>
              <Button onClick={() => handleProjectAction(currentProject)}>Resume Project</Button>
            </div>
            <div className="flex items-center justify-center">
              <div className="text-center">
                <div className="text-6xl font-bold text-primary-600 mb-2">
                  {Math.round(Number(currentProject.progress_percentage ?? currentProject.progress ?? 0))}%
                </div>
                <p className="text-secondary-600">Complete</p>
              </div>
            </div>
          </div>
        ) : (
          <p className="text-secondary-600">No projects yet. Generate one to start your personalized path.</p>
        )}
      </div>

      {/* Recommended Projects */}
      <ProjectTabs activeTab={activeTab} onTabChange={setActiveTab}>
        {activeTab === 'recommended' && filteredProjects.length === 0 && (
          <div className="mb-6 flex items-center justify-between gap-4 p-4 bg-secondary-50 rounded-lg border border-secondary-200">
            <p className="text-sm text-secondary-700">No recommendations found yet. Generate AI recommendations now.</p>
            <Button onClick={handleGenerateRecommendations} disabled={isGenerating}>
              {isGenerating ? 'Generating...' : 'Generate Recommendations'}
            </Button>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProjects.map((project) => (
            <ProjectCard
              key={project._id || project.id}
              project={project}
              onAction={handleProjectAction}
            />
          ))}
        </div>
        {filteredProjects.length === 0 && (
          <p className="text-sm text-secondary-500">No projects match this filter yet.</p>
        )}
      </ProjectTabs>
    </div>
  );
};

export default ProjectsPage;
