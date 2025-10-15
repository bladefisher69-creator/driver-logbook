import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage } from './components/auth/LoginPage';
import { RegisterPage } from './components/auth/RegisterPage';
import { Layout } from './components/Layout';
import { DriverDashboard } from './components/dashboard/DriverDashboard';
import { AdminDashboard } from './components/admin/AdminDashboard';
import { TripsPage } from './components/trips/TripsPage';
import { FuelPage } from './components/fuel/FuelPage';

const AppContent: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const [authView, setAuthView] = useState<'login' | 'register'>('login');
  const [currentPage, setCurrentPage] = useState('dashboard');

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
          <p className="mt-4 text-slate-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return authView === 'login' ? (
      <LoginPage onSwitchToRegister={() => setAuthView('register')} />
    ) : (
      <RegisterPage onSwitchToLogin={() => setAuthView('login')} />
    );
  }

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return user?.is_admin ? <AdminDashboard /> : <DriverDashboard />;
      case 'trips':
        return <TripsPage />;
      case 'fuel':
        return <FuelPage />;
      case 'drivers':
        return <AdminDashboard />;
      case 'compliance':
        return <AdminDashboard />;
      default:
        return user?.is_admin ? <AdminDashboard /> : <DriverDashboard />;
    }
  };

  return (
    <Layout currentPage={currentPage} onNavigate={setCurrentPage}>
      {renderPage()}
    </Layout>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
