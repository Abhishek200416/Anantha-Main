import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('anantha-token'));
  const [loading, setLoading] = useState(true);

  // Set axios default header
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API}/auth/register`, userData);
      const { user, token } = response.data;
      
      setUser(user);
      setToken(token);
      localStorage.setItem('anantha-token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Registration failed' 
      };
    }
  };

  const login = async (credentials) => {
    try {
      const response = await axios.post(`${API}/auth/login`, credentials);
      const { user, token } = response.data;
      
      setUser(user);
      setToken(token);
      localStorage.setItem('anantha-token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const googleLogin = async (idToken) => {
    try {
      const response = await axios.post(`${API}/auth/google`, { id_token: idToken });
      const { user, token } = response.data;
      
      setUser(user);
      setToken(token);
      localStorage.setItem('anantha-token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Google login failed' 
      };
    }
  };

  const sendPhoneOTP = async (phone) => {
    try {
      const response = await axios.post(`${API}/auth/phone/send-otp`, { phone });
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Failed to send OTP' 
      };
    }
  };

  const verifyPhoneOTP = async (phone, otp) => {
    try {
      const response = await axios.post(`${API}/auth/phone/verify-otp`, { phone, otp });
      const { user, token } = response.data;
      
      setUser(user);
      setToken(token);
      localStorage.setItem('anantha-token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'OTP verification failed' 
      };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('anantha-token');
    delete axios.defaults.headers.common['Authorization'];
  };

  const isAuthenticated = !!user;

  return (
    <AuthContext.Provider value={{
      user,
      token,
      loading,
      isAuthenticated,
      register,
      login,
      googleLogin,
      sendPhoneOTP,
      verifyPhoneOTP,
      logout
    }}>
      {children}
    </AuthContext.Provider>
  );
};
