import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { User, Lock, Eye, EyeOff, UserCheck } from 'lucide-react';

const CleaningLogin = () => {
  const navigate = useNavigate();
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post('http://localhost:8001/api/cleaning/auth/login', credentials);
      
      // Store token and user info
      localStorage.setItem('cleaning_token', response.data.access_token);
      localStorage.setItem('cleaning_user_type', response.data.user_type);
      localStorage.setItem('cleaning_team_id', response.data.team_id);
      localStorage.setItem('cleaning_role', response.data.role);

      // Redirect to cleaning dashboard
      navigate('/cleaning/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      setError(error.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-metro-primary to-metro-secondary flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-12 w-12 bg-white rounded-full flex items-center justify-center">
            <UserCheck className="h-8 w-8 text-metro-primary" />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            Cleaning Team Login
          </h2>
          <p className="mt-2 text-center text-sm text-metro-100">
            Access your cleaning assignments and photo evaluation system
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div className="relative">
              <label htmlFor="username" className="sr-only">
                Username
              </label>
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <User className="h-5 w-5 text-gray-400" />
              </div>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 pl-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-metro-primary focus:border-metro-primary focus:z-10 sm:text-sm"
                placeholder="Username"
                value={credentials.username}
                onChange={handleInputChange}
              />
            </div>
            <div className="relative">
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
              </div>
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 pl-10 pr-10 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-metro-primary focus:border-metro-primary focus:z-10 sm:text-sm"
                placeholder="Password"
                value={credentials.password}
                onChange={handleInputChange}
              />
              <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                <button
                  type="button"
                  className="text-gray-400 hover:text-gray-500"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5" />
                  ) : (
                    <Eye className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-700">{error}</div>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-metro-primary hover:bg-metro-secondary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-metro-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
              ) : (
                'Sign in to Cleaning Dashboard'
              )}
            </button>
          </div>

          <div className="text-center">
            <button
              type="button"
              onClick={() => navigate('/management/login')}
              className="text-metro-100 hover:text-white text-sm underline"
            >
              Back to Management Login
            </button>
          </div>
        </form>

        {/* Demo Credentials */}
        <div className="mt-6 bg-white/10 backdrop-blur rounded-lg p-4">
          <h3 className="text-white font-medium mb-2">Demo Credentials:</h3>
          <div className="text-metro-100 text-sm space-y-1">
            <p><strong>Team Leader:</strong> cleaner1 / password123</p>
            <p><strong>Cleaner:</strong> cleaner2 / password123</p>
            <p><strong>Supervisor:</strong> supervisor1 / password123</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CleaningLogin;