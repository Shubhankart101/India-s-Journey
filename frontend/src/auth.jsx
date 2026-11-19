import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { api } from './api.js';

const STORAGE_KEY = 'ij_auth_user';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        const item = window.localStorage.getItem(STORAGE_KEY);
        return item ? JSON.parse(item) : null;
      } catch {
        return null;
      }
    }
    return null;
  });
  const [ready, setReady] = useState(() => {
    if (typeof window !== 'undefined' && window.localStorage) {
      return Boolean(window.localStorage.getItem(STORAGE_KEY));
    }
    return false;
  });

  const refresh = useCallback(async () => {
    try {
      const data = await api.me();
      if (data?.authenticated && data?.user) {
        setUser(data.user);
        if (typeof window !== 'undefined' && window.localStorage) {
          try {
            window.localStorage.setItem(STORAGE_KEY, JSON.stringify(data.user));
          } catch {}
        }
      } else if (data?.user) {
        setUser(data.user);
      } else {
        const local = typeof window !== 'undefined' && window.localStorage ? window.localStorage.getItem(STORAGE_KEY) : null;
        if (local) {
          try {
            setUser(JSON.parse(local));
          } catch {
            setUser(null);
          }
        } else {
          setUser(null);
        }
      }
    } catch {
      const local = typeof window !== 'undefined' && window.localStorage ? window.localStorage.getItem(STORAGE_KEY) : null;
      if (local) {
        try {
          setUser(JSON.parse(local));
        } catch {
          setUser(null);
        }
      } else {
        setUser(null);
      }
    } finally {
      setReady(true);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const login = useCallback(userData => {
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(userData));
      } catch {}
    }
    setUser(userData);
  }, []);

  const logout = useCallback(async () => {
    if (typeof window !== 'undefined' && window.localStorage) {
      try {
        window.localStorage.removeItem(STORAGE_KEY);
      } catch {}
    }
    try {
      await api.logout();
    } catch {
      // ignore
    }
    setUser(null);
  }, []);

  const value = useMemo(() => ({ user, ready, login, logout, refresh }), [user, ready, login, logout, refresh]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => {
  const value = useContext(AuthContext);
  if (!value) {
    // Graceful fallback if rendered outside AuthProvider in isolated tests
    return { user: null, ready: true, login: () => {}, logout: async () => {}, refresh: async () => {} };
  }
  return value;
};
