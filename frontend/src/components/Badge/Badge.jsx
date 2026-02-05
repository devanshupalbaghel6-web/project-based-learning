import React from 'react';
import { clsx } from 'clsx';

/**
 * Badge Component
 * @param {object} props
 * @param {React.ReactNode} props.children - Badge content
 * @param {'primary' | 'success' | 'warning' | 'error'} props.variant - Badge color variant
 * @param {string} props.className - Additional CSS classes
 */
const Badge = ({
  children,
  variant = 'primary',
  className = '',
  ...props
}) => {
  const variantClasses = {
    primary: 'badge-primary',
    success: 'badge-success',
    warning: 'badge-warning',
    error: 'badge-error',
  };

  return (
    <span
      className={clsx(
        'badge',
        variantClasses[variant],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
};

export default Badge;
