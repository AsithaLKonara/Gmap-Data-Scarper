import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import MainLayout from './components/MainLayout';

const Dashboard = lazy(() => import('./pages/Dashboard'));
// const Projects = lazy(() => import('./pages/ProjectDashboard'));
const Teams = lazy(() => import('./pages/TeamManagement'));
const Settings = lazy(() => import('./pages/Settings'));
const WorkspaceSetup = lazy(() => import('./pages/WorkspaceSetup'));
const NotFound = lazy(() => import('./pages/NotFound'));
const APIDocumentation = lazy(() => import('./components/APIDocumentation'));
const Webhooks = lazy(() => import('./pages/Webhooks'));
const Integrations = lazy(() => import('./pages/Integrations'));
const Widgets = lazy(() => import('./pages/Widgets'));
const SsoCallback = lazy(() => import('./pages/SsoCallback'));
const AdminAuditLog = lazy(() => import('./pages/AdminAuditLog'));

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/sso/callback" element={<SsoCallback />} />
          <Route path="/" element={<MainLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            {/* <Route path="projects" element={<Projects />} /> */}
            <Route path="teams" element={<Teams />} />
            {/* <Route path="copilot" element={<Copilot />} /> */}
            <Route path="settings" element={<Settings />} />
            <Route path="workspace-setup" element={<WorkspaceSetup />} />
            {/* <Route path="project-wizard" element={<ProjectWizard />} /> */}
            <Route path="api" element={<APIDocumentation />} />
            <Route path="webhooks" element={<Webhooks />} />
            <Route path="integrations" element={<Integrations />} />
            <Route path="widgets" element={<Widgets />} />
            <Route path="admin/audit-log" element={<AdminAuditLog />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
};

export default App; 