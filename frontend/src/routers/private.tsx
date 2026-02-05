// 需登入
import HomePage from '../pages/Home'
import AuthGuard from './guards'
import AuthLayout from '../layouts/AuthLayout'

const PrivateRoutes = [{
  element: <AuthLayout />,
    children: [
        {
          path: '/home',
          element: (
            <AuthGuard>
              <HomePage />
            </AuthGuard>
          ),
        }
    ],
}]

export default PrivateRoutes
