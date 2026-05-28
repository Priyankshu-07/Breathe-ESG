import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

const API_BASE = 'https://breathe-esg-hw2p.onrender.com';

interface User {
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('breathe_token');
    const storedUser = localStorage.getItem('breathe_user');
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setIsLoading(false);
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE}/api/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) return false;

      const data = await response.json();
      const authToken = data.token;

      const userObj: User = {
        email: username,
        name: username.split('@')[0] || username,
      };

      setToken(authToken);
      setUser(userObj);
      localStorage.setItem('breathe_token', authToken);
      localStorage.setItem('breathe_user', JSON.stringify(userObj));
      return true;
    } catch (err) {
      return false;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('breathe_token');
    localStorage.removeItem('breathe_user');
  };

  return (
    <AuthContext.Provider value={{
      user, token, isAuthenticated: !!token, login, logout, isLoading,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) throw new Error('useAuth must be used within an AuthProvider');
  return context;
}

export { API_BASE };