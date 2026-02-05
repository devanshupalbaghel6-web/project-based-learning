import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  FolderKanban,
  BookOpen,
  Map,
  MessageCircle,
  Settings,
} from 'lucide-react';
import { clsx } from 'clsx';

const navigationItems = [
  { name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
  { name: 'Projects', icon: FolderKanban, path: '/projects' },
  { name: 'Resources', icon: BookOpen, path: '/resources' },
  { name: 'Roadmaps', icon: Map, path: '/roadmaps' },
  { name: 'AI Chatbot', icon: MessageCircle, path: '/chatbot' },
  { name: 'Settings', icon: Settings, path: '/settings' },
];

/**
 * Sidebar Component
 * @param {object} props
 * @param {boolean} props.isOpen - Sidebar open state (mobile)
 */
const Sidebar = ({ isOpen = true }) => {
  const location = useLocation();

  return (
    <aside
      className={clsx(
        'sidebar',
        !isOpen && '-translate-x-full lg:translate-x-0'
      )}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-6 border-b border-secondary-800">
        <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-lg flex items-center justify-center">
          <span className="text-white font-bold text-xl">AL</span>
        </div>
        <div>
          <h2 className="font-heading font-bold text-lg">AI-Learn Hub</h2>
          <p className="text-xs text-secondary-400">Learn by Building</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-6">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          
          return (
            <Link
              key={item.name}
              to={item.path}
              className={clsx(
                'sidebar-item',
                isActive && 'sidebar-item-active'
              )}
            >
              <Icon size={20} />
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Profile */}
      <div className="border-t border-secondary-800 p-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
            <span className="text-white font-semibold">AC</span>
          </div>
          <div className="flex-1">
            <p className="font-medium text-sm">Alex Chen</p>
            <p className="text-xs text-secondary-400">alex@example.com</p>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
