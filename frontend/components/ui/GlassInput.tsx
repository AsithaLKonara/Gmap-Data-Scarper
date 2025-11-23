import React from 'react';
import { useRouter } from 'next/router';

interface GlassInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  darkMode?: boolean; // Allow explicit dark mode control
}

export default function GlassInput({
  label,
  error,
  helperText,
  className = '',
  darkMode,
  ...props
}: GlassInputProps) {
  const router = useRouter();
  
  // Check if we're on a dark background (video background pages)
  const isDarkBackground = darkMode !== undefined 
    ? darkMode 
    : router.pathname === '/login' || 
      router.pathname === '/signup' || 
      router.pathname === '/landing';

  return (
    <div className="w-full">
      {label && (
        <label className={`block text-sm font-medium mb-2 ${
          isDarkBackground ? 'text-white/90' : 'text-gray-700 dark:text-gray-300'
        }`}>
          {label}
        </label>
      )}
      <input
        className={`
          w-full px-4 py-2 rounded-lg transition-all
          ${error 
            ? 'border-red-400/50 focus:border-red-400' 
            : isDarkBackground 
              ? 'border-white/20 focus:border-white/40' 
              : 'border-gray-300 dark:border-gray-600 focus:border-primary/50'
          }
          ${isDarkBackground 
            ? 'text-white placeholder:text-white/60 bg-white/10 backdrop-blur-sm focus:bg-white/15 focus:ring-2 focus:ring-white/30' 
            : 'bg-white/10 backdrop-blur-sm border-gray-300 dark:border-gray-600 text-gray-900 dark:text-gray-100 placeholder:text-gray-500 dark:placeholder:text-gray-400 focus:bg-white/15 dark:focus:bg-gray-800/50'
          }
          focus:outline-none
          ${className}
        `}
        {...props}
      />
      {error && (
        <p className={`mt-1 text-sm animate-fade-in ${
          isDarkBackground ? 'text-red-400' : 'text-red-500'
        }`}>{error}</p>
      )}
      {helperText && !error && (
        <p className={`mt-1 text-sm ${
          isDarkBackground ? 'text-white/80' : 'text-gray-500 dark:text-gray-400'
        }`}>{helperText}</p>
      )}
    </div>
  );
}

