import { createBrowserRouter } from 'react-router-dom'
// import IndexPage from '../pages/Index'
// import LoginPage from '../pages/Login'
// import HomePage from '../pages/Home'
// import AuthLayout from '../layouts/AuthLayout'

import PublicRoutes from './public'
import PrivateRoutes from './private'

// router 入口(統一管理)
export const router = createBrowserRouter([
    ...PublicRoutes,
    ...PrivateRoutes
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
])