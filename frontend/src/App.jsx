import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from '@components/Sidebar';
import Header from '@components/Header';

// Pages
import OnboardingPage from '@pages/Onboarding';
import DashboardPage from '@pages/Dashboard';
import ProjectsPage from '@pages/Projects';
import ResourcesPage from '@pages/Resources';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <Router>
      <Routes>
        {/* Onboarding Route - No Layout */}
        <Route path="/onboarding" element={<OnboardingPage />} />

        {/* Main App Routes - With Layout */}
        <Route
          path="/*"
          element={
            <div className="flex min-h-screen bg-secondary-50">
              {/* Sidebar */}
              <Sidebar isOpen={sidebarOpen} />

              {/* Main Content */}
              <div className="flex-1 lg:ml-64">
                <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
                
                <main className="container-custom py-8">
                  <Routes>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/dashboard" element={<DashboardPage />} />
                    <Route path="/projects" element={<ProjectsPage />} />
                    <Route path="/resources" element={<ResourcesPage />} />
                    <Route path="/roadmaps" element={<div>Roadmaps Page (Coming Soon)</div>} />
                    <Route path="/chatbot" element={<div>AI Chatbot Page (Coming Soon)</div>} />
                    <Route path="/settings" element={<div>Settings Page (Coming Soon)</div>} />
                  </Routes>
                </main>
              </div>
            </div>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
