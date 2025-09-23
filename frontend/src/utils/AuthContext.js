import React, { createContext, useState, useContext, useEffect } from 'react';
import { authAPI, setAuthToken, getAuthToken } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    initializeAuth();
  }, []);

  const initializeAuth = async () => {
    console.log('Initializing authentication...');
    const token = getAuthToken();
    if (token) {
      console.log('Token found, verifying...');
      try {
        const userData = await authAPI.getCurrentUser();
        console.log('Token valid, user data:', userData);
        setUser(userData);
        setIsAuthenticated(true);
      } catch (error) {
        console.log('Token invalid, clearing storage');
        // Token is invalid, remove it
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    } else {
      console.log('No token found');
    }
    setLoading(false);
  };

  const login = async (username, password) => {
    try {
      console.log('Attempting login for:', username);
      const response = await authAPI.login(username, password);
      const { access_token } = response;
      
      console.log('Login successful, token received');
      setAuthToken(access_token);
      
      // Get user details
      console.log('Fetching user details...');
      const userData = await authAPI.getCurrentUser();
      console.log('User data received:', userData);
      
      setUser(userData);
      setIsAuthenticated(true);
      
      // Store user data in localStorage for persistence
      localStorage.setItem('user', JSON.stringify(userData));
      
      console.log('Login completed successfully');
      return { success: true, user: userData };
    } catch (error) {
      console.error('Login error:', error);
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Login failed' 
      };
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
      setAuthToken(null);
      localStorage.removeItem('user');
    }
  };

  const hasRole = (requiredRoles) => {
    if (!user) return false;
    
    if (Array.isArray(requiredRoles)) {
      return requiredRoles.includes(user.role);
    }
    
    return user.role === requiredRoles;
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    hasRole
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};