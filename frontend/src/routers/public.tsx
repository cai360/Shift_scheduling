// NoLogin
import LoginPage from '../pages/Login';
import IndexPage from '../pages/Index';
import AuthLayout from '../layouts/AuthLayout';

const PublicRoutes = [
  {
    element: <AuthLayout />,
    children: [
      {
        path: '/',
        element: <IndexPage />,
      },
      {
        path: '/login',
        element: <LoginPage />,
      },
    ],
  },
];

export default PublicRoutes;
