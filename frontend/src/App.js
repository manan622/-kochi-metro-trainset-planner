import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './utils/AuthContext';
import LoginPage from './pages/LoginPage';
import ManagementPortal from './pages/ManagementPortal';
import InspectionPortal from './pages/InspectionPortal';
import WorkerPortal from './pages/WorkerPortal';
import FleetDashboard from './pages/FleetDashboard';
import TrainsetDetail from './pages/TrainsetDetail';
import LoadingSpinner from './components/LoadingSpinner';

// Protected Route Component
const ProtectedRoute = ({ children, requiredRoles = null }) => {
  const { isAuthenticated, user, loading, hasRole } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRoles && !hasRole(requiredRoles)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
};

// Role-based redirect component
const RoleBasedRedirect = () => {
  const { user } = useAuth();

  if (!user) return <Navigate to="/login" replace />;

  switch (user.role) {
    case 'management':
      return <Navigate to="/management" replace />;
    case 'inspection':
      return <Navigate to="/inspection" replace />;
    case 'worker':
      return <Navigate to="/worker" replace />;
    default:
      return <Navigate to="/login" replace />;
  }
};

const AppContent = () => {
  const { loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<LoginPage />} />
      
      {/* Root redirect based on role */}
      <Route path="/" element={<RoleBasedRedirect />} />
      
      {/* Role-based portals */}
      <Route 
        path="/management" 
        element={
          <ProtectedRoute requiredRoles={['management']}>
            <ManagementPortal />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/inspection" 
        element={
          <ProtectedRoute requiredRoles={['management', 'inspection']}>
            <InspectionPortal />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/worker" 
        element={
          <ProtectedRoute requiredRoles={['management', 'inspection', 'worker']}>
            <WorkerPortal />
          </ProtectedRoute>
        } 
      />
      
      {/* Shared protected routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <FleetDashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/trainset/:trainsetId" 
        element={
          <ProtectedRoute>
            <TrainsetDetail />
          </ProtectedRoute>
        } 
      />
      
      {/* Unauthorized page */}
      <Route 
        path="/unauthorized" 
        element={
          <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">Unauthorized</h1>
              <p className="text-gray-600 mb-8">You don't have permission to access this page.</p>
              <button 
                onClick={() => window.history.back()}
                className="bg-metro-primary text-white px-6 py-2 rounded-lg hover:bg-metro-secondary transition-colors"
              >
                Go Back
              </button>
            </div>
          </div>
        } 
      />
      
      {/* 404 page */}
      <Route 
        path="*" 
        element={
          <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-4">Page Not Found</h1>
              <p className="text-gray-600 mb-8">The page you're looking for doesn't exist.</p>
              <button 
                onClick={() => window.location.href = '/'}
                className="bg-metro-primary text-white px-6 py-2 rounded-lg hover:bg-metro-secondary transition-colors"
              >
                Go Home
              </button>
            </div>
          </div>
        } 
      />
    </Routes>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppContent />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;