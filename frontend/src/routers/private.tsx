// Login
import HomePage from '../pages/Home';
import AuthGuard from './guards';
import AuthLayout from '../layouts/AuthLayout';
import NewCompanyPage from '../pages/NewCompany';
import MembersPage from '../pages/Members';

const PrivateRoutes = [
  {
    element: (
      <AuthGuard>
        <AuthLayout />
      </AuthGuard>
    ),
    children: [
      { path: '/home', element: <HomePage /> },
      { path: '/new-company', element: <NewCompanyPage /> },
      { path: '/members', element: <MembersPage /> },
    ],
  },
];

export default PrivateRoutes;
