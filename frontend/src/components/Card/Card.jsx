import React from 'react';
import { clsx } from 'clsx';

/**
 * Card Component
 * @param {object} props
 * @param {React.ReactNode} props.children - Card content
 * @param {boolean} props.hoverable - Enable hover effect
 * @param {string} props.className - Additional CSS classes
 */
const Card = ({
  children,
  hoverable = false,
  className = '',
  onClick,
  ...props
}) => {
  return (
    <div
      className={clsx(
        'card',
        hoverable && 'card-hover cursor-pointer',
        className
      )}
      onClick={onClick}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
