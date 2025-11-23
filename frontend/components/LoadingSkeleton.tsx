import React from 'react';

interface LoadingSkeletonProps {
  variant?: 'text' | 'circular' | 'rectangular' | 'card';
  width?: string | number;
  height?: string | number;
  className?: string;
  lines?: number;
}

export default function LoadingSkeleton({
  variant = 'rectangular',
  width,
  height,
  className = '',
  lines = 1,
}: LoadingSkeletonProps) {
  const baseClasses = 'glass-subtle rounded-glass-md shimmer animate-pulse';

  if (variant === 'card') {
    return (
      <div className={`${baseClasses} p-6 space-y-4 ${className}`}>
        <div className="h-6 glass-subtle rounded w-3/4 shimmer"></div>
        <div className="h-4 glass-subtle rounded w-full shimmer"></div>
        <div className="h-4 glass-subtle rounded w-5/6 shimmer"></div>
      </div>
    );
  }

  if (variant === 'text') {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={`${baseClasses} h-4`}
            style={{
              width: width || (i === lines - 1 ? '60%' : '100%'),
            }}
          />
        ))}
      </div>
    );
  }

  if (variant === 'circular') {
    return (
      <div
        className={`${baseClasses} rounded-full`}
        style={{
          width: width || 40,
          height: height || 40,
        }}
      />
    );
  }

  // rectangular (default)
  return (
    <div
      className={baseClasses}
      style={{
        width: width || '100%',
        height: height || 20,
      }}
    />
  );
}

