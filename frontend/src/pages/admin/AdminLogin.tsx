import axios from 'axios'
import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../../features/admin/auth-context'
import type { ApiErrorBody } from '../../types/api'

function loginError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as ApiErrorBody | undefined
    return body?.error?.message ?? 'Unable to sign in. Try again.'
  }
  return 'Unable to sign in. Try again.'
}

export default function AdminLogin() {
  const { token, login } = useAuth()
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (token) {
    return <Navigate to="/change-data" replace />
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await login(password)
      navigate('/change-data', { replace: true })
    } catch (loginFailure) {
      setError(loginError(loginFailure))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="admin-login">
      <div className="admin-login-card">
        <div className="admin-login-head">
          <Link className="admin-wordmark" to="/">
            SP<span>.</span>
          </Link>
          <p className="admin-kicker">Private workspace</p>
        </div>
        <h1>Change the data.</h1>
        <p className="admin-login-lede">
          Sign in to edit the profile, projects, experience, and notes that power the public site.
        </p>
        <form className="admin-login-form" onSubmit={handleSubmit}>
          <label className="field">
            <span>Password</span>
            <input
              autoComplete="current-password"
              autoFocus
              name="password"
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Enter your admin password"
              required
              type="password"
              value={password}
            />
          </label>
          {error ? (
            <p className="admin-status admin-status--error" role="alert">
              {error}
            </p>
          ) : null}
          <button
            className="button button--primary admin-submit"
            disabled={submitting}
            type="submit"
          >
            {submitting ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
        <Link className="admin-back-link" to="/">
          Back to the public site
        </Link>
      </div>
    </main>
  )
}
