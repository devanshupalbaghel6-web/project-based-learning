import React from 'react';

/**
 * Loading Spinner Component
 * @param {object} props
 * @param {string} props.size - Spinner size (sm, md, lg)
 * @param {string} props.className - Additional CSS classes
 */
const Spinner = ({ size = 'md', className = '' }) => {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-4',
    lg: 'w-12 h-12 border-4',
  };

  return (
    <div
      className={`inline-block border-secondary-300 border-t-primary-600 rounded-full animate-spin ${sizeClasses[size]} ${className}`}
    />
  );
};

export default Spinner;
