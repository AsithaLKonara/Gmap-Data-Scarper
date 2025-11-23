import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getCurrentUser, refreshToken } from '../utils/api';

interface User {
  user_id: string;
  email: string;
}

interface UserContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshAuth: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Only run on client side
    if (typeof window === 'undefined') {
      setLoading(false);
      return;
    }

    // Check for existing token and validate
    const accessToken = localStorage.getItem('access_token');
    const refreshTokenValue = localStorage.getItem('refresh_token');
    
    if (accessToken) {
      // Try to get current user
      getCurrentUser()
        .then((userData) => {
          setUser(userData);
        })
        .catch(() => {
          // Token invalid, try refresh
          if (refreshTokenValue) {
            refreshToken(refreshTokenValue)
              .then((tokens) => {
                localStorage.setItem('access_token', tokens.access_token);
                localStorage.setItem('refresh_token', tokens.refresh_token);
                return getCurrentUser();
              })
              .then((userData) => {
                setUser(userData);
              })
              .catch(() => {
                // Refresh failed, clear tokens
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                setUser(null);
              });
          } else {
            setUser(null);
          }
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email: string, password: string) => {
    if (typeof window === 'undefined') {
      throw new Error('Login can only be called on client side');
    }
    
    const { login: loginApi } = await import('../utils/api');
    const tokens = await loginApi({ email, password });
    
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    localStorage.setItem('user_email', email);
    
    const userData = await getCurrentUser();
    setUser(userData);
  };

  const logout = () => {
    if (typeof window === 'undefined') return;
    
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_email');
    setUser(null);
  };

  const refreshAuth = async () => {
    if (typeof window === 'undefined') {
      throw new Error('Refresh auth can only be called on client side');
    }
    
    const refreshTokenValue = localStorage.getItem('refresh_token');
    if (!refreshTokenValue) {
      throw new Error('No refresh token available');
    }
    
    const tokens = await refreshToken(refreshTokenValue);
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    
    const userData = await getCurrentUser();
    setUser(userData);
  };

  return (
    <UserContext.Provider value={{ user, loading, login, logout, refreshAuth }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
}

