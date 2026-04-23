import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import authService from '@services/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => localStorage.getItem('token'));
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const persistToken = (nextToken) => {
    if (nextToken) {
      localStorage.setItem('token', nextToken);
    } else {
      localStorage.removeItem('token');
    }
    setToken(nextToken);
  };

  const refreshUser = async () => {
    const currentToken = localStorage.getItem('token');
    if (!currentToken) {
      setUser(null);
      return null;
    }

    try {
      const profile = await authService.getCurrentUser();
      setUser(profile);
      return profile;
    } catch (error) {
      persistToken(null);
      setUser(null);
      return null;
    }
  };

  useEffect(() => {
    let mounted = true;

    const bootstrap = async () => {
      setIsLoading(true);
      await refreshUser();
      if (mounted) {
        setIsLoading(false);
      }
    };

    bootstrap();

    return () => {
      mounted = false;
    };
  }, [token]);

  const register = async (payload) => {
    const authPayload = await authService.register(payload);
    persistToken(authPayload.access_token);
    await refreshUser();
    return authPayload;
  };

  const login = async (payload) => {
    const authPayload = await authService.login(payload);
    persistToken(authPayload.access_token);
    await refreshUser();
    return authPayload;
  };

  const logout = () => {
    persistToken(null);
    setUser(null);
  };

  const value = useMemo(
    () => ({
      token,
      user,
      isLoading,
      isAuthenticated: Boolean(token),
      register,
      login,
      logout,
      refreshUser,
    }),
    [token, user, isLoading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return context;
};
