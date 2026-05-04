// routers/AppRouter.tsx
import { useEffect } from 'react';
import { useNavigate, Outlet } from 'react-router-dom';
import { setUnauthorizedHandler } from '../utils/http';

const AppRouter = () => {
  const navigate = useNavigate();

  useEffect(() => {
    setUnauthorizedHandler(() => {
      navigate('/login', { replace: true });
    });
  }, [navigate]);

  return <Outlet />;
};

export default AppRouter;
