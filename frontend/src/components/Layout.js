import React from 'react';
import { useAuth } from '../utils/AuthContext';
import { Train, LogOut, User, BarChart3 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const Layout = ({ children, title }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'management':
        return 'bg-purple-100 text-purple-800';
      case 'inspection':
        return 'bg-blue-100 text-blue-800';
      case 'worker':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="h-10 w-10 bg-metro-primary rounded-lg flex items-center justify-center mr-3">
                <Train className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Kochi Metro Induction Planner
                </h1>
                <p className="text-sm text-gray-500">{title}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
              >
                <BarChart3 className="h-4 w-4 mr-2" />
                Dashboard
              </button>
              
              <div className="flex items-center space-x-3">
                <div className="flex items-center">
                  <User className="h-4 w-4 text-gray-400 mr-2" />
                  <span className="text-sm font-medium text-gray-900">{user?.username}</span>
                  <span className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${getRoleColor(user?.role)}`}>
                    {user?.role}
                  </span>
                </div>
                
                <button
                  onClick={handleLogout}
                  className="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-red-600 transition-colors"
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
};

export default Layout;