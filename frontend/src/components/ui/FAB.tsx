import React from 'react';
import { cn } from '@/lib/utils';

interface FABProps {
  icon: React.ReactNode;
  label?: string;
  onClick: () => void;
  className?: string;
}

export const FAB: React.FC<FABProps> = ({ icon, label, onClick, className }) => (
  <button
    type="button"
    onClick={onClick}
    className={cn(
      'fixed bottom-8 right-8 z-50 flex items-center gap-2 px-5 py-3 rounded-full bg-primary text-primary-foreground shadow-lg hover:bg-primary/90 active:scale-95 transition-all focus:outline-none focus:ring-2 focus:ring-primary',
      className
    )}
    aria-label={label || 'Quick action'}
  >
    {icon}
    {label && <span className="font-semibold text-base hidden sm:inline">{label}</span>}
  </button>
); 