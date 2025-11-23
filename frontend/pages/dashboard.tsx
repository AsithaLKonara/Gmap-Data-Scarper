import React, { lazy, Suspense } from 'react';
import GradientBackground from '../components/ui/GradientBackground';
import LoadingSkeleton from '../components/LoadingSkeleton';

// Lazy load dashboard component
const Dashboard = lazy(() => import('../components/Dashboard'));

export default function DashboardPage() {
  return (
    <GradientBackground variant="clean">
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6 text-gradient-primary">Analytics Dashboard</h1>
        <Suspense fallback={<LoadingSkeleton variant="card" className="h-96" />}>
          <Dashboard />
        </Suspense>
      </div>
    </GradientBackground>
  );
}

