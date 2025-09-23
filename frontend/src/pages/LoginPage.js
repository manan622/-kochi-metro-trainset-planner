import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import { authAPI } from '../services/api';
import { Train, User, Lock, Info } from 'lucide-react';

const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [availableUsers, setAvailableUsers] = useState([]);
  const [showUserList, setShowUserList] = useState(false);
  
  const { isAuthenticated, login } = useAuth();

  useEffect(() => {
    // Fetch available users for demo purposes
    const fetchUsers = async () => {
      try {
        const response = await authAPI.getAvailableUsers();
        setAvailableUsers(response.available_users || []);
      } catch (error) {
        console.error('Failed to fetch users:', error);
      }
    };
    
    fetchUsers();
  }, []);

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await login(username, password);
      if (!result.success) {
        setError(result.error);
      }
    } catch (error) {
      setError('An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleUserSelect = (user) => {
    setUsername(user.username);
    setPassword(user.password);
    setShowUserList(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-metro-primary to-metro-secondary flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-20 w-20 bg-white rounded-full flex items-center justify-center shadow-lg">
            <Train className="h-10 w-10 text-metro-primary" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            Kochi Metro
          </h2>
          <p className="mt-2 text-center text-sm text-blue-100">
            Trainset Induction Planner
          </p>
        </div>
        
        <form className="mt-8 space-y-6 bg-white p-8 rounded-xl shadow-xl" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-800">{error}</p>
                </div>
              </div>
            </div>
          )}
          
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="username" className="sr-only">Username</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  className="relative block w-full pl-10 pr-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-metro-primary focus:border-metro-primary focus:z-10 sm:text-sm"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
            </div>
            <div>
              <label htmlFor="password" className="sr-only">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  className="relative block w-full pl-10 pr-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-metro-primary focus:border-metro-primary focus:z-10 sm:text-sm"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-3 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-metro-primary hover:bg-metro-secondary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-metro-primary disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
          
          {/* Demo Users Section */}
          <div className="mt-6 border-t pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Info className="h-4 w-4 text-gray-400 mr-2" />
                <span className="text-sm text-gray-600">Demo Users</span>
              </div>
              <button
                type="button"
                onClick={() => setShowUserList(!showUserList)}
                className="text-sm text-metro-primary hover:text-metro-secondary"
              >
                {showUserList ? 'Hide' : 'Show'}
              </button>
            </div>
            
            {showUserList && availableUsers.length > 0 && (
              <div className="mt-3 space-y-2">
                {availableUsers.map((user, index) => (
                  <div
                    key={index}
                    onClick={() => handleUserSelect(user)}
                    className="cursor-pointer p-3 border border-gray-200 rounded-md hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <span className="font-medium text-gray-900">{user.username}</span>
                        <span className="ml-2 text-sm text-gray-500">({user.role})</span>
                      </div>
                      <span className="text-xs text-gray-400">{user.password}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage;