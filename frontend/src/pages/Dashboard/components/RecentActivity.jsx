import React from 'react';
import Card from '@components/Card';

const ActivityItem = ({ activity }) => (
  <div className="flex items-start gap-3 pb-4 last:pb-0">
    <div className={`w-2 h-2 rounded-full mt-2 ${
      activity.type === 'completed' ? 'bg-success-DEFAULT' :
      activity.type === 'started' ? 'bg-primary-600' :
      'bg-warning-DEFAULT'
    }`}></div>
    <div className="flex-1">
      <p className="text-sm font-medium text-secondary-900">{activity.title}</p>
      <p className="text-xs text-secondary-500 mt-1">{activity.time}</p>
    </div>
  </div>
);

const RecentActivity = () => {
  const activities = [
    { id: 1, type: 'completed', title: 'Completed Module: Intro to NLP', time: '2 hours ago' },
    { id: 2, type: 'started', title: 'Started Project: Sentiment Analysis', time: '1 day ago' },
    { id: 3, type: 'milestone', title: 'Reached Checkpoint 3: Data Collection', time: '2 days ago' },
    { id: 4, type: 'completed', title: 'Completed Resource: PyTorch Tutorial', time: '3 days ago' },
  ];

  return (
    <Card>
      <h3 className="font-heading font-semibold text-xl mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {activities.map((activity) => (
          <ActivityItem key={activity.id} activity={activity} />
        ))}
      </div>
    </Card>
  );
};

export default RecentActivity;
