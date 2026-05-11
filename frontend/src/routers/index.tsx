import { createBrowserRouter } from 'react-router-dom';
// import IndexPage from '../pages/Index'
// import LoginPage from '../pages/Login'
// import HomePage from '../pages/Home'
// import AuthLayout from '../layouts/AuthLayout'
import AppRouter from './appRouter';
import PublicRoutes from './public';
import PrivateRoutes from './private';

// router Entrance (Unified Management)
export const router = createBrowserRouter([
  {
    element: <AppRouter />,
    children: [...PublicRoutes, ...PrivateRoutes],
  },
  // {
  //     element: <AuthLayout />,
  //     children: [
  //         {
  //             path: '/',
  //             element: <IndexPage />
  //         },
  //         {
  //             path: '/login',
  //             element: <LoginPage />
  //         },
  //         {
  //             path: '/home',
  //             element: <HomePage />
  //         }
  //     ]
  // }
]);
