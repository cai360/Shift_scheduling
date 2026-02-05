// 權限控制
import { Navigate } from 'react-router-dom'
import type { JSX } from 'react'

const AuthGuard = ({ children }: { children: JSX.Element }) => {
  const isLogin = Boolean(localStorage.getItem('token'))

  if (!isLogin) {
    return <Navigate to="/login" replace />
  }

  return children
}

export default AuthGuard