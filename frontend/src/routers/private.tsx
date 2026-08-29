// Login
import HomePage from '../pages/Home';
import AuthGuard from './guards';
import AuthLayout from '../layouts/AuthLayout';
import NewCompanyPage from '../pages/NewCompany';
import MembersPage from '../pages/Members';
import ShiftManagementPage from '../pages/ShiftManagementPage';
import ProfilePage from '../pages/ProfilePage';
import EditProfilePage from '../pages/EditProfilePage';
import AccountSettingsPage from '../pages/AccountSettingsPage';

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
      { path: '/shift-management', element: <ShiftManagementPage /> },
      { path: '/profile', element: <ProfilePage /> },
      { path: '/profile/edit', element: <EditProfilePage /> },
      { path: '/account-settings', element: <AccountSettingsPage /> },
    ],
  },
];

export default PrivateRoutes;
