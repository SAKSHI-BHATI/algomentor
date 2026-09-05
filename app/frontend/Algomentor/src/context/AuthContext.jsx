import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('algomentor_token') || null);
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('algomentor_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [isAuthenticated, setIsAuthenticated] = useState(() => !!token);
  const [loading, setLoading] = useState(true);

  // Validate existing token on mount
  useEffect(() => {
    const verifyToken = async () => {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const res = await fetch(`${BASE_URL}/auth/me`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });
        const data = await res.json();
        if (data.success && data.user) {
          setUser(data.user);
          setIsAuthenticated(true);
          localStorage.setItem('algomentor_user', JSON.stringify(data.user));
        } else {
          logout();
        }
      } catch (err) {
        console.warn("Auth verification warning:", err);
      } finally {
        setLoading(false);
      }
    };
    verifyToken();
  }, [token]);

  const login = async (email, password) => {
    try {
      const res = await fetch(`${BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (!data.success) {
        throw new Error(data.detail || data.error || "Login failed");
      }
      
      setToken(data.token);
      setUser(data.user);
      setIsAuthenticated(true);
      localStorage.setItem('algomentor_token', data.token);
      localStorage.setItem('algomentor_user', JSON.stringify(data.user));
      return { success: true };
    } catch (err) {
      // Do not create a local-only session: protected endpoints would reject it.
      throw err;
    }
  };

  const register = async (email, password, name) => {
    try {
      const res = await fetch(`${BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, name })
      });
      const data = await res.json();
      if (!data.success) {
        throw new Error(data.detail || data.error || "Registration failed");
      }
      
      setToken(data.token);
      setUser(data.user);
      setIsAuthenticated(true);
      localStorage.setItem('algomentor_token', data.token);
      localStorage.setItem('algomentor_user', JSON.stringify(data.user));
      return { success: true };
    } catch (err) {
      throw err;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('algomentor_token');
    localStorage.removeItem('algomentor_user');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, token, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
