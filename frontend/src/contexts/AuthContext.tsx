import React, { createContext, useContext, useState, useCallback } from 'react';
import type { 
  User, 
  LoginRequest, 
  RegisterRequest, 
  TokenResponse, 
  TwoFAEnableResponse,
  AuthContextType 
} from '../types/auth';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('jarvis_token'));
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (credentials: LoginRequest): Promise<TokenResponse> => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `username=${encodeURIComponent(credentials.username)}&password=${encodeURIComponent(credentials.password)}`,
      });
      if (!res.ok) throw new Error('Invalid credentials');
      const data: TokenResponse = await res.json();
      localStorage.setItem('jarvis_token', data.access_token);
      setToken(data.access_token);
      return data;
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Login failed');
      throw e;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (data: RegisterRequest): Promise<void> => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_URL}/register?username=${encodeURIComponent(data.username)}&password=${encodeURIComponent(data.password)}`, {
        method: 'POST',
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Registration failed');
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Registration failed');
      throw e;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('jarvis_token');
    setToken(null);
    setUser(null);
  }, []);

  const enable2FA = useCallback(async (): Promise<TwoFAEnableResponse> => {
    const res = await fetch(`${API_URL}/auth/2fa/enable`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Failed to enable 2FA');
    return res.json();
  }, [token]);

  const verify2FA = useCallback(async (code: string): Promise<void> => {
    const res = await fetch(`${API_URL}/auth/2fa/verify?code=${encodeURIComponent(code)}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!res.ok) throw new Error('Invalid 2FA code');
  }, [token]);

  const refreshToken = useCallback(async (): Promise<void> => {
    if (!token) return;
    const res = await fetch(`${API_URL}/refresh`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
    });
    if (!res.ok) {
      logout();
      return;
    }
    const data: TokenResponse = await res.json();
    localStorage.setItem('jarvis_token', data.access_token);
    setToken(data.access_token);
  }, [token, logout]);

  return (
    <AuthContext.Provider value={{
      user,
      token,
      isAuthenticated: !!token,
      isLoading,
      error,
      login,
      register,
      logout,
      enable2FA,
      verify2FA,
      refreshToken,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
