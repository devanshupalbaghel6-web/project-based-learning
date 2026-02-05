import React from 'react';
import { clsx } from 'clsx';

/**
 * ProgressBar Component
 * @param {object} props
 * @param {number} props.value - Progress value (0-100)
 * @param {string} props.className - Additional CSS classes
 * @param {boolean} props.showLabel - Show percentage label
 */
const ProgressBar = ({
  value = 0,
  className = '',
  showLabel = false,
  ...props
}) => {
  const clampedValue = Math.min(Math.max(value, 0), 100);

  return (
    <div className="w-full">
      <div className={clsx('progress-bar', className)} {...props}>
        <div
          className="progress-bar-fill"
          style={{ width: `${clampedValue}%` }}
        />
      </div>
      {showLabel && (
        <div className="mt-1 text-sm text-secondary-600 text-right">
          {clampedValue}%
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
