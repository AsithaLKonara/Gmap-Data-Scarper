import React from 'react';

interface GradientBackgroundProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'success' | 'warm' | 'cool' | 'purple' | 'clean';
  className?: string;
}

export default function GradientBackground({
  children,
  variant = 'clean',
  className = '',
}: GradientBackgroundProps) {
  const variantClasses = {
    primary: 'bg-gradient-primary',
    secondary: 'bg-gradient-secondary',
    success: 'bg-gradient-success',
    warm: 'bg-gradient-warm',
    cool: 'bg-gradient-cool',
    purple: 'bg-gradient-purple',
    clean: 'gradient-clean',
  };

  return (
    <div className={`min-h-screen ${variantClasses[variant]} ${className}`}>
      {children}
    </div>
  );
}

