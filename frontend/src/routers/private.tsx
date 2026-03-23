// Login
import HomePage from '../pages/Home';
import AuthGuard from './guards';
import AuthLayout from '../layouts/AuthLayout';
import NewCompanyPage from '../pages/NewCompany';

const PrivateRoutes = [
  {
    element: <AuthLayout />,
    children: [
      {
        path: '/home',
        element: (
          <AuthGuard>
            <HomePage />
          </AuthGuard>
        ),
      },
      {
        path: '/new-company',
        element: (
          <AuthGuard>
            <NewCompanyPage />
          </AuthGuard>
        ),
      },
    ],
  },
];

export default PrivateRoutes;
