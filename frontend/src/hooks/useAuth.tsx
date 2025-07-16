import React, { createContext, useContext, useState, useEffect } from 'react';
import * as api from '../api';

type User = {
  id: number;
  email: string;
  plan: string;
  role?: string; // legacy single role
  roles?: string[]; // new: multiple roles
  permissions?: string[]; // new: granular permissions
  isAdmin?: boolean;
};

type LoginResult = { type: 'success' } | { type: '2fa', userId: number };

type AuthContextType = {
  user: User | null;
  login: (email: string, password: string) => Promise<LoginResult>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
  error: string | null;
  hasRole: (role: string) => boolean;
  hasPermission: (perm: string) => boolean;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const t = localStorage.getItem('token');
    if (t) {
      api.setToken(t);
      api.getUser().then(u => {
        // Support both legacy and new RBAC
        setUser(u ? {
          ...u,
          isAdmin: u.plan === 'business' || (u.roles && u.roles.includes('admin')),
          roles: u.roles || (u.role ? [u.role] : []),
          permissions: u.permissions || [],
        } : null);
      }).catch(() => setUser(null)).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string): Promise<LoginResult> => {
    setError(null);
    setLoading(true);
    try {
      const data = await api.login(email, password);
      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        api.setToken(data.access_token);
        const u = await api.getUser();
        setUser(u ? { ...u, isAdmin: u.plan === 'business' } : null);
        return { type: 'success' };
      } else if (data.two_fa_required || data["2fa_required"]) {
        // 2FA required, return info to UI
        return { type: '2fa', userId: Number(data.user_id) };
      } else {
        throw new Error('Unknown login response');
      }
    } catch (e: any) {
      setError(e.message);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  const register = async (email: string, password: string) => {
    setError(null);
    setLoading(true);
    try {
      await api.register(email, password);
      await login(email, password);
    } catch (e: any) {
      setError(e.message);
      throw e;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    api.setToken(null);
    setUser(null);
  };

  // RBAC helpers
  const hasRole = (role: string) => {
    return user?.roles?.includes(role) || user?.role === role;
  };
  const hasPermission = (perm: string) => {
    return !!user?.permissions && user.permissions.includes(perm);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading, error, hasRole, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
} 