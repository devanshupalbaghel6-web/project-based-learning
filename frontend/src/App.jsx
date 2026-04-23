import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from '@components/Sidebar';
import Header from '@components/Header';
import Spinner from '@components/Spinner';
import { useAuth } from '@/context/AuthContext';

// Pages
import AuthPage from '@pages/Auth';
import OnboardingPage from '@pages/Onboarding';
import DashboardPage from '@pages/Dashboard';
import ProjectsPage from '@pages/Projects';
import ResourcesPage from '@pages/Resources';
import RoadmapsPage from '@pages/Roadmaps';
import ChatbotPage from '@pages/Chatbot';
import SettingsPage from '@pages/Settings';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-secondary-50">
        <Spinner size="lg" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  return children;
};

const PublicRoute = ({ children }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-secondary-50">
        <Spinner size="lg" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to={user?.onboarding_completed ? '/dashboard' : '/onboarding'} replace />;
  }

  return children;
};

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { user, logout } = useAuth();

  return (
    <Router>
      <Routes>
        <Route
          path="/auth"
          element={
            <PublicRoute>
              <AuthPage />
            </PublicRoute>
          }
        />

        <Route
          path="/onboarding"
          element={
            <ProtectedRoute>
              <OnboardingPage />
            </ProtectedRoute>
          }
        />

        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <div className="flex min-h-screen bg-secondary-50">
                <Sidebar
                  isOpen={sidebarOpen}
                  currentUser={user}
                  onLogout={logout}
                  onNavigate={() => setSidebarOpen(false)}
                />
                {sidebarOpen && (
                  <div
                    className="fixed inset-0 bg-black/40 z-30 lg:hidden"
                    onClick={() => setSidebarOpen(false)}
                  />
                )}

                <div className="flex-1 lg:ml-64">
                  <Header
                    onMenuClick={() => setSidebarOpen(!sidebarOpen)}
                    currentUser={user}
                    onLogout={logout}
                  />

                  <main className="container-custom py-8">
                    <Routes>
                      <Route
                        path="/"
                        element={<Navigate to={user?.onboarding_completed ? '/dashboard' : '/onboarding'} replace />}
                      />
                      <Route path="/dashboard" element={<DashboardPage />} />
                      <Route path="/projects" element={<ProjectsPage />} />
                      <Route path="/resources" element={<ResourcesPage />} />
                      <Route path="/roadmaps" element={<RoadmapsPage />} />
                      <Route path="/chatbot" element={<ChatbotPage />} />
                      <Route path="/settings" element={<SettingsPage />} />
                      <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                  </main>
                </div>
              </div>
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
