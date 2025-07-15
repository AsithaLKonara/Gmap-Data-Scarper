import React from 'react';
import Navbar from './Navbar';
import SidebarLeft from './SidebarLeft';
import Footer from './Footer';
import { Breadcrumbs } from './ui/breadcrumbs';
import { Outlet } from 'react-router-dom';
import { FAB } from './ui/FAB';
import { Plus } from 'lucide-react';

const MainLayout: React.FC = () => {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <Navbar />
      <div className="flex flex-1 pt-16">
        <SidebarLeft onJobCreated={() => {}} />
        <div className="flex-1 flex flex-col">
          <div className="px-4 sm:px-8 pt-4">
            <Breadcrumbs />
          </div>
          <main className="flex-1 px-4 sm:px-8 py-4">
            <Outlet />
          </main>
          <Footer />
        </div>
      </div>
      <FAB icon={<Plus className="w-5 h-5" />} label="Add Lead" onClick={() => alert('Quick action: Add Lead!')} />
    </div>
  );
};

export default MainLayout; 