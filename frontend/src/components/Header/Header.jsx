import React from 'react';
import { Search, Bell, Menu } from 'lucide-react';

/**
 * Header Component
 * @param {object} props
 * @param {function} props.onMenuClick - Menu toggle handler
 * @param {object} props.currentUser - Authenticated user
 * @param {function} props.onLogout - Logout handler
 */
const Header = ({ onMenuClick, currentUser, onLogout }) => {
  const name = currentUser?.name || currentUser?.full_name || 'User';
  const initials = name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  return (
    <header className="bg-white border-b border-secondary-200 sticky top-0 z-30">
      <div className="flex items-center justify-between px-4 lg:px-8 py-4">
        {/* Left Section */}
        <div className="flex items-center gap-4 flex-1">
          <button
            onClick={onMenuClick}
            className="lg:hidden text-secondary-600 hover:text-secondary-900"
          >
            <Menu size={24} />
          </button>

          {/* Search Bar */}
          <div className="hidden md:flex items-center gap-3 bg-secondary-100 rounded-lg px-4 py-2 flex-1 max-w-xl">
            <Search size={20} className="text-secondary-400" />
            <input
              type="text"
              placeholder="Search projects, resources..."
              className="bg-transparent border-none outline-none flex-1 text-sm"
            />
          </div>
        </div>

        {/* Right Section */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <button className="relative p-2 hover:bg-secondary-100 rounded-lg transition-colors">
            <Bell size={20} className="text-secondary-600" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-error-DEFAULT rounded-full"></span>
          </button>

          {/* Avatar */}
          <div className="hidden sm:flex flex-col items-end">
            <p className="text-sm font-semibold text-secondary-800">{name}</p>
            <button
              type="button"
              className="text-xs text-secondary-500 hover:text-secondary-700"
              onClick={() => onLogout?.()}
            >
              Sign out
            </button>
          </div>

          <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center cursor-pointer hover:ring-2 ring-primary-300 transition-all">
            <span className="text-white font-semibold text-sm">{initials}</span>
          </div>
        </div>
      </div>

      {/* Mobile Search */}
      <div className="md:hidden px-4 pb-4">
        <div className="flex items-center gap-3 bg-secondary-100 rounded-lg px-4 py-2">
          <Search size={20} className="text-secondary-400" />
          <input
            type="text"
            placeholder="Search..."
            className="bg-transparent border-none outline-none flex-1 text-sm"
          />
        </div>
      </div>
    </header>
  );
};

export default Header;
