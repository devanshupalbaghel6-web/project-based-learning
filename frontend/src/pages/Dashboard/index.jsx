import React, { useEffect, useMemo, useState } from 'react';
import { DashboardStats, RecentActivity } from './components';
import Card from '@components/Card';
import Button from '@components/Button';
import Spinner from '@components/Spinner';
import { Calendar, ArrowRight } from 'lucide-react';
import projectsService from '@services/projects';
import progressService from '@services/progress';
import { useAuth } from '@/context/AuthContext';

const DashboardPage = () => {
  const cleanText = (value = '') =>
    String(value).replace(/\*\*/g, '').replace(/^title:\s*/i, '').trim();
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [activities, setActivities] = useState([]);
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;

    const loadDashboardData = async () => {
      setIsLoading(true);
      setError('');

      try {
        const [projectsData, statsData, recentActivity] = await Promise.all([
          projectsService.getProjects(null, 0, 25),
          progressService.getStats(),
          progressService.getRecentActivity(7),
        ]);

        if (!mounted) {
          return;
        }

        setProjects(Array.isArray(projectsData) ? projectsData : []);
        setStats(statsData);
        setActivities(recentActivity?.activities || []);
      } catch (loadError) {
        if (!mounted) {
          return;
        }
        setError('Unable to load dashboard data right now.');
      } finally {
        if (mounted) {
          setIsLoading(false);
        }
      }
    };

    loadDashboardData();

    return () => {
      mounted = false;
    };
  }, []);

  const currentProject = useMemo(() => {
    if (!projects.length) {
      return null;
    }

    return projects.find((item) => item.status === 'in_progress') || projects[0];
  }, [projects]);

  const upcomingDeadlines = useMemo(
    () =>
      activities.slice(0, 3).map((item, index) => ({
        id: item._id || index,
        title: item.action ? item.action.replace(/_/g, ' ') : 'Activity',
        date: item.timestamp ? new Date(item.timestamp).toLocaleDateString() : 'Today',
      })),
    [activities]
  );

  const projectProgress = Math.round(
    Number(currentProject?.progress_percentage ?? currentProject?.progress ?? 0)
  );

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
      <div>
        <h1 className="font-heading font-bold text-3xl mb-2">
          Welcome back, {user?.name || user?.full_name || 'Learner'}! 👋
        </h1>
        <p className="text-secondary-600">
          Here's what's happening with your learning journey today
        </p>
        {error && <p className="text-sm text-error-DEFAULT mt-2">{error}</p>}
      </div>

      {/* Stats */}
      <DashboardStats stats={stats} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Current Project */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <h2 className="font-heading font-semibold text-2xl mb-4">
              Continue Learning
            </h2>
            <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-xl p-6 border border-primary-200">
              {currentProject ? (
                <>
                  <h3 className="font-heading font-bold text-xl mb-2">{cleanText(currentProject.title)}</h3>
                  <p className="text-secondary-700 mb-4">{currentProject.description}</p>
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm font-medium">Overall Progress</span>
                    <span className="text-sm font-bold text-primary-600">{projectProgress}%</span>
                  </div>
                  <div className="w-full bg-white rounded-full h-3 mb-4">
                    <div
                      className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full"
                      style={{ width: `${projectProgress}%` }}
                    ></div>
                  </div>
                  <div className="flex gap-3">
                    <Button>Continue Project</Button>
                    <Button variant="outline">View Roadmap</Button>
                  </div>
                </>
              ) : (
                <p className="text-secondary-700">No active project yet. Generate one from the Projects page.</p>
              )}
            </div>
          </Card>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card hoverable className="cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-lg mb-1">Explore Projects</h3>
                  <p className="text-sm text-secondary-600">Find your next challenge</p>
                </div>
                <ArrowRight className="text-primary-600" size={24} />
              </div>
            </Card>
            <Card hoverable className="cursor-pointer">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-lg mb-1">Browse Resources</h3>
                  <p className="text-sm text-secondary-600">Curated learning materials</p>
                </div>
                <ArrowRight className="text-primary-600" size={24} />
              </div>
            </Card>
          </div>
        </div>

        {/* Right Column - Sidebar Content */}
        <div className="space-y-6">
          {/* Upcoming Deadlines */}
          <Card>
            <div className="flex items-center gap-2 mb-4">
              <Calendar className="text-primary-600" size={20} />
              <h3 className="font-heading font-semibold text-lg">Quick Actions</h3>
            </div>
            <div className="space-y-3">
              {upcomingDeadlines.map((deadline) => (
                <div key={deadline.id} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                  <div className="flex-1">
                    <p className="font-medium text-sm">{deadline.title}</p>
                  </div>
                  <span className="text-xs font-semibold text-primary-600 bg-primary-100 px-2 py-1 rounded">
                    {deadline.date}
                  </span>
                </div>
              ))}
              {upcomingDeadlines.length === 0 && (
                <p className="text-sm text-secondary-500">No recent actions yet.</p>
              )}
            </div>
          </Card>

          {/* Recent Activity */}
          <RecentActivity activities={activities} />
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
