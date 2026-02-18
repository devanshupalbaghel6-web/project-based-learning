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
            change.startsWith('+') ? 'text-success-DEFAULT' : 'text-error-DEFAULT'
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

const DashboardStats = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatCard
        icon={Target}
        title="Active Projects"
        value="3"
        change="+1 this week"
        color="bg-primary-600"
      />
      <StatCard
        icon={Award}
        title="Completed"
        value="12"
        change="+2 this month"
        color="bg-success-DEFAULT"
      />
      <StatCard
        icon={Calendar}
        title="Days Streak"
        value="15"
        change="+5 days"
        color="bg-warning-DEFAULT"
      />
      <StatCard
        icon={TrendingUp}
        title="Avg Progress"
        value="68%"
        change="+12%"
        color="bg-primary-600"
      />
    </div>
  );
};

export default DashboardStats;
