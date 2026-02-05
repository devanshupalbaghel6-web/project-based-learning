import React from 'react';
import { clsx } from 'clsx';

/**
 * Input Component
 * @param {object} props
 * @param {string} props.label - Input label
 * @param {string} props.type - Input type
 * @param {string} props.placeholder - Placeholder text
 * @param {string} props.error - Error message
 * @param {string} props.helperText - Helper text below input
 * @param {string} props.value - Input value
 * @param {function} props.onChange - Change handler
 * @param {boolean} props.required - Required field
 * @param {string} props.className - Additional CSS classes
 */
const Input = React.forwardRef(({
  label,
  type = 'text',
  placeholder,
  error,
  helperText,
  value,
  onChange,
  required = false,
  className = '',
  ...props
}, ref) => {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-secondary-700 mb-2">
          {label}
          {required && <span className="text-error-DEFAULT ml-1">*</span>}
        </label>
      )}
      <input
        ref={ref}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={clsx(
          'input',
          error && 'input-error',
          className
        )}
        {...props}
      />
      {error && (
        <p className="mt-2 text-sm text-error-DEFAULT">{error}</p>
      )}
      {helperText && !error && (
        <p className="mt-2 text-sm text-secondary-500">{helperText}</p>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;
