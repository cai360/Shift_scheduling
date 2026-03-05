// NoLogin
import LoginPage from '../pages/Login';
// import IndexPage from '../pages/Index';
import RegisterPage from '../pages/Register';
import ForgetPage from '../pages/Forget';
import EmptyLayout from '../layouts/EmptyLayout';

const PublicRoutes = [
  {
    element: <EmptyLayout />,
    children: [
      // {
      //   path: '/',
      //   element: <IndexPage />,
      // },
      {
        path: '/login',
        element: <LoginPage />,
      },
      {
        path: '/register',
        element: <RegisterPage />,
      },
      {
        path: '/forget-password',
        element: <ForgetPage />,
      },
    ],
  },
];

export default PublicRoutes;
