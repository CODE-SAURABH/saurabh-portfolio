import { useCallback, useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { apiClient, clearToken, readToken, writeToken } from '../../lib/apiClient'
import type { ApiData } from '../../types/api'
import { AuthContext } from './auth-context'

interface LoginResponse {
  access_token: string
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => readToken())

  useEffect(() => {
    const handleExpired = () => setToken(null)
    window.addEventListener('sp-auth-expired', handleExpired)
    return () => window.removeEventListener('sp-auth-expired', handleExpired)
  }, [])

  const login = useCallback(async (password: string) => {
    const response = await apiClient.post<ApiData<LoginResponse>>('/admin/auth/login', {
      password,
    })
    const nextToken = response.data.data.access_token
    writeToken(nextToken)
    setToken(nextToken)
  }, [])

  const logout = useCallback(async () => {
    try {
      await apiClient.post('/admin/auth/logout')
    } catch {
      clearToken()
    }
    clearToken()
    setToken(null)
  }, [])

  return <AuthContext.Provider value={{ token, login, logout }}>{children}</AuthContext.Provider>
}
