import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  onClick?: () => void;
}

export default function GlassCard({ 
  children, 
  className = '', 
  hover = true,
  onClick 
}: GlassCardProps) {
  return (
    <div
      className={`
        glass rounded-glass-lg p-6
        ${hover ? 'hover-lift cursor-pointer' : ''}
        ${onClick ? 'cursor-pointer' : ''}
        transition-all duration-300
        ${className}
      `}
      onClick={onClick}
    >
      {children}
    </div>
  );
}

