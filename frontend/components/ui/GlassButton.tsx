import React from 'react';

interface GlassButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  gradient?: boolean;
  children: React.ReactNode;
}

export default function GlassButton({
  variant = 'primary',
  size = 'md',
  gradient = false,
  children,
  className = '',
  disabled,
  ...props
}: GlassButtonProps) {
  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg',
  };

  const variantClasses = {
    primary: gradient 
      ? 'bg-gradient-primary text-white' 
      : 'glass text-primary border-primary/20',
    secondary: gradient
      ? 'bg-gradient-secondary text-white'
      : 'glass text-secondary border-secondary/20',
    success: gradient
      ? 'bg-gradient-success text-white'
      : 'glass text-success border-success/20',
    warning: 'glass text-warning border-warning/20',
    error: 'glass text-error border-error/20',
  };

  return (
    <button
      className={`
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        rounded-xl font-medium
        border transition-all duration-300
        hover:scale-105 hover:shadow-glass-lg
        active:scale-95
        disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
        ${className}
      `}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}

