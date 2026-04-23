import React from 'react';
import Card from '@components/Card';

const formatRelativeTime = (timestamp) => {
  if (!timestamp) return 'Just now';
  const eventDate = new Date(timestamp);
  const now = new Date();
  const diffMs = Math.max(now.getTime() - eventDate.getTime(), 0);
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);

  if (diffHours < 1) return 'Less than an hour ago';
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
};

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

const RecentActivity = ({ activities = [] }) => {
  const mappedActivities = activities.map((item, index) => ({
    id: item._id || item.id || index,
    type: item.action?.includes('completed') ? 'completed' : item.action?.includes('started') ? 'started' : 'milestone',
    title: item.action ? item.action.replace(/_/g, ' ') : 'Activity',
    time: formatRelativeTime(item.timestamp),
  }));

  return (
    <Card>
      <h3 className="font-heading font-semibold text-xl mb-4">Recent Activity</h3>
      <div className="space-y-4">
        {mappedActivities.length === 0 && (
          <p className="text-sm text-secondary-500">No recent activity yet. Start a project to see your timeline.</p>
        )}
        {mappedActivities.map((activity) => (
          <ActivityItem key={activity.id} activity={activity} />
        ))}
      </div>
    </Card>
  );
};

export default RecentActivity;
