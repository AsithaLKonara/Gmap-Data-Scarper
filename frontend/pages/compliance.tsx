import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import ComplianceDashboard from '../components/ComplianceDashboard';
import GradientBackground from '../components/ui/GradientBackground';
import GlassButton from '../components/ui/GlassButton';

export default function CompliancePage() {
  const router = useRouter();

  return (
    <GradientBackground variant="clean">
      <div className="min-h-screen">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="mb-6">
            <GlassButton
              onClick={() => router.push('/')}
              variant="secondary"
              size="sm"
              className="mb-4"
            >
              ← Back to Dashboard
            </GlassButton>
            <h1 className="text-3xl font-bold text-gradient-primary mb-2">Data Compliance</h1>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Manage data retention, opt-out requests, and compliance settings
            </p>
          </div>
          <ComplianceDashboard />
        </div>
      </div>
    </GradientBackground>
  );
}

