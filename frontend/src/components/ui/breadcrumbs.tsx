import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

export const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter(Boolean);

  return (
    <nav className="flex items-center text-sm text-muted-foreground py-2" aria-label="Breadcrumb">
      <Link to="/" className="hover:text-foreground font-medium">Home</Link>
      {pathnames.map((segment, idx) => {
        const to = '/' + pathnames.slice(0, idx + 1).join('/');
        const isLast = idx === pathnames.length - 1;
        return (
          <span key={to} className="flex items-center">
            <ChevronRight className="mx-2 w-4 h-4" />
            {isLast ? (
              <span className="text-foreground font-semibold capitalize">{decodeURIComponent(segment.replace(/-/g, ' '))}</span>
            ) : (
              <Link to={to} className="hover:text-foreground capitalize">{decodeURIComponent(segment.replace(/-/g, ' '))}</Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}; 