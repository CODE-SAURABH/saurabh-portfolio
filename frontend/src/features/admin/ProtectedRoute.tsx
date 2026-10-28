import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './auth-context'

export function ProtectedRoute() {
  const { token } = useAuth()

  if (!token) {
    return <Navigate to="/change-data/login" replace />
  }

  return <Outlet />
}
