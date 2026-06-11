import { useState, useEffect } from 'react';
import { getMe } from '../services/auth.api';
import { AuthContext, AuthContextType, User } from './AuthContext';

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthInitializing, setIsAuthInitializing] = useState(true);

  const restoreUser = async () => {
    const meRes = await getMe();
    setUser(meRes);
  };

  useEffect(() => {
    const bootstrap = async () => {
      const token = localStorage.getItem('access_token');

      if (!token) {
        setIsAuthInitializing(false);
        return;
      }

      try {
        await restoreUser();
      } catch {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
      } finally {
        setIsAuthInitializing(false);
      }
    };

    bootstrap();
  }, []);

  const value: AuthContextType = {
    user,
    setUser,
    isAuthInitializing,
    restoreUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
