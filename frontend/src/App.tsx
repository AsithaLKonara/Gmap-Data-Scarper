import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/MainLayout';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Projects = lazy(() => import('./pages/ProjectDashboard'));
const Teams = lazy(() => import('./pages/TeamManagement'));
const Copilot = lazy(() => import('./pages/Copilot'));
const Settings = lazy(() => import('./pages/Settings'));
const WorkspaceSetup = lazy(() => import('./pages/WorkspaceSetup'));
const ProjectWizard = lazy(() => import('./pages/ProjectWizard'));
const NotFound = lazy(() => import('./pages/NotFound'));

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="projects" element={<Projects />} />
            <Route path="teams" element={<Teams />} />
            <Route path="copilot" element={<Copilot />} />
            <Route path="settings" element={<Settings />} />
            <Route path="workspace-setup" element={<WorkspaceSetup />} />
            <Route path="project-wizard" element={<ProjectWizard />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
};

export default App; 