import React from 'react';
import Card from '@components/Card';
import { Calendar, TrendingUp, Target, Award } from 'lucide-react';

const StatCard = ({ icon: Icon, title, value, change, color }) => (
  <Card>
    <div className="flex items-center justify-between">
      <div>
        <p className="text-secondary-600 text-sm mb-1">{title}</p>
        <h3 className="text-2xl font-bold mb-1">{value}</h3>
        {change && (
          <p className={`text-sm flex items-center gap-1 ${
            change.startsWith('+')
              ? 'text-success-DEFAULT'
              : change.startsWith('-')
                ? 'text-error-DEFAULT'
                : 'text-secondary-600'
          }`}>
            <TrendingUp size={14} />
            {change}
          </p>
        )}
      </div>
      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${color}`}>
        <Icon className="text-white" size={24} />
      </div>
    </div>
  </Card>
);

const DashboardStats = ({ stats }) => {
  const activeProjects = stats?.total_projects ?? 0;
  const completedMilestones = stats?.completed_milestones ?? 0;
  const streak = stats?.longest_streak ?? 0;
  const completionRate = Math.round((stats?.completion_rate ?? 0) * 100);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        icon={Target}
        title="Active Projects"
        value={String(activeProjects)}
        change={activeProjects > 0 ? 'In progress' : null}
        color="bg-primary-600"
      />
      <StatCard
        icon={Award}
        title="Milestones Done"
        value={String(completedMilestones)}
        change={completedMilestones > 0 ? 'Completed so far' : null}
        color="bg-success-DEFAULT"
      />
      <StatCard
        icon={Calendar}
        title="Days Streak"
        value={String(streak)}
        change={streak > 0 ? 'Keep it up' : null}
        color="bg-warning-DEFAULT"
      />
      <StatCard
        icon={TrendingUp}
        title="Completion Rate"
        value={`${completionRate}%`}
        change={completionRate > 0 ? 'Across checkpoints' : null}
        color="bg-primary-600"
      />
    </div>
  );
};

export default DashboardStats;
