import { createContext, useContext, useState, useEffect } from 'react';
import { getMe } from '../services/auth.api';

type User = {
  id: string;
  username: string;
  email: string;
};

type AuthContextType = {
  user: User | null;
  setUser: (user: User | null) => void;
  isAuthInitializing: boolean;
  restoreUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);


export const AuthProvider = ({ children, }: {children: React.ReactNode;}) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthInitializing, setIsAuthInitializing] = useState(true);
  
  const restoreUser = async () => {
    const meRes = await getMe();
    setUser(meRes.data);
  }

  useEffect(()=>{
   const bootstrap = async () => {
    const token = localStorage.getItem('token');

    if(!token){
      setIsAuthInitializing(false);
      return;
    }

    try{
      await restoreUser();
    } catch (error) {
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    } finally {
      setIsAuthInitializing(false);
    }
   };

   bootstrap();
  }, []);

  return (
    <AuthContext.Provider value={{ user, setUser, isAuthInitializing, restoreUser}}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuthContext = () => {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error('useAuthContext must be used within AuthProvider');
  }

  return context;
};