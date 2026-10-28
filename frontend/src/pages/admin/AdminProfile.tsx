import axios from 'axios'
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { apiClient } from '../../lib/apiClient'
import type { ApiData, ApiErrorBody } from '../../types/api'
import type { Profile, ProfileFormValues } from '../../types/profile'

const emptyForm: ProfileFormValues = {
  full_name: '',
  headline: '',
  bio: '',
  location: '',
  email: '',
  github_url: '',
  linkedin_url: '',
  website_url: '',
  avatar_url: '',
  availability_note: '',
}

function toForm(profile: Profile): ProfileFormValues {
  return {
    full_name: profile.full_name,
    headline: profile.headline,
    bio: profile.bio ?? '',
    location: profile.location ?? '',
    email: profile.email ?? '',
    github_url: profile.github_url ?? '',
    linkedin_url: profile.linkedin_url ?? '',
    website_url: profile.website_url ?? '',
    avatar_url: profile.avatar_url ?? '',
    availability_note: profile.availability_note ?? '',
  }
}

function nullable(value: string): string | null {
  const trimmed = value.trim()
  return trimmed ? trimmed : null
}

function requestError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as ApiErrorBody | undefined
    return body?.error?.message ?? 'The profile could not be saved.'
  }
  return 'The profile could not be saved.'
}

export default function AdminProfile() {
  const [form, setForm] = useState<ProfileFormValues>(emptyForm)
  const [exists, setExists] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    apiClient
      .get<ApiData<Profile>>('/admin/profile')
      .then((response) => {
        if (!active) return
        setForm(toForm(response.data.data))
        setExists(true)
      })
      .catch((loadError: unknown) => {
        if (!active) return
        if (axios.isAxiosError(loadError) && loadError.response?.status === 404) {
          setExists(false)
          return
        }
        setError(requestError(loadError))
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  const updateField = (field: keyof ProfileFormValues, value: string) => {
    setForm((current) => ({ ...current, [field]: value }))
    setMessage(null)
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError(null)
    setMessage(null)

    const payload = {
      full_name: form.full_name.trim(),
      headline: form.headline.trim(),
      bio: nullable(form.bio),
      location: nullable(form.location),
      email: nullable(form.email),
      github_url: nullable(form.github_url),
      linkedin_url: nullable(form.linkedin_url),
      website_url: nullable(form.website_url),
      avatar_url: nullable(form.avatar_url),
      availability_note: nullable(form.availability_note),
    }

    try {
      const response = exists
        ? await apiClient.patch<ApiData<Profile>>('/admin/profile', payload)
        : await apiClient.put<ApiData<Profile>>('/admin/profile', payload)
      setForm(toForm(response.data.data))
      setExists(true)
      setMessage('Profile saved.')
    } catch (saveError) {
      setError(requestError(saveError))
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return <p className="admin-loading">Loading profile...</p>
  }

  return (
    <section className="admin-page">
      <div className="admin-page-head admin-page-head--row">
        <div>
          <p className="admin-kicker">Profile</p>
          <h1>
            The public <span className="accent">identity.</span>
          </h1>
          <p className="admin-page-lede">
            These fields feed the home page, about page, metadata, and contact details.
          </p>
        </div>
        <Link className="button button--small" to="/">
          Preview site
        </Link>
      </div>

      <form className="admin-form" onSubmit={handleSubmit}>
        <div className="admin-form-section">
          <div>
            <p className="admin-form-label">Core</p>
            <p className="admin-form-hint">The first thing a visitor reads.</p>
          </div>
          <div className="form-grid">
            <label className="field">
              <span>Full name</span>
              <input
                maxLength={120}
                onChange={(event) => updateField('full_name', event.target.value)}
                required
                value={form.full_name}
              />
            </label>
            <label className="field">
              <span>Headline</span>
              <input
                maxLength={200}
                onChange={(event) => updateField('headline', event.target.value)}
                required
                value={form.headline}
              />
            </label>
            <label className="field field--full">
              <span>Biography</span>
              <textarea
                onChange={(event) => updateField('bio', event.target.value)}
                rows={6}
                value={form.bio}
              />
            </label>
            <label className="field">
              <span>Location</span>
              <input
                maxLength={100}
                onChange={(event) => updateField('location', event.target.value)}
                value={form.location}
              />
            </label>
            <label className="field">
              <span>Availability note</span>
              <input
                maxLength={200}
                onChange={(event) => updateField('availability_note', event.target.value)}
                value={form.availability_note}
              />
            </label>
          </div>
        </div>

        <div className="admin-form-section">
          <div>
            <p className="admin-form-label">Contact and links</p>
            <p className="admin-form-hint">Public URLs only. Empty fields are hidden.</p>
          </div>
          <div className="form-grid">
            <label className="field">
              <span>Email</span>
              <input
                onChange={(event) => updateField('email', event.target.value)}
                type="email"
                value={form.email}
              />
            </label>
            <label className="field">
              <span>GitHub URL</span>
              <input
                maxLength={500}
                onChange={(event) => updateField('github_url', event.target.value)}
                type="url"
                value={form.github_url}
              />
            </label>
            <label className="field">
              <span>LinkedIn URL</span>
              <input
                maxLength={500}
                onChange={(event) => updateField('linkedin_url', event.target.value)}
                type="url"
                value={form.linkedin_url}
              />
            </label>
            <label className="field">
              <span>Website URL</span>
              <input
                maxLength={500}
                onChange={(event) => updateField('website_url', event.target.value)}
                type="url"
                value={form.website_url}
              />
            </label>
            <label className="field field--full">
              <span>Avatar URL</span>
              <input
                maxLength={500}
                onChange={(event) => updateField('avatar_url', event.target.value)}
                type="url"
                value={form.avatar_url}
              />
            </label>
          </div>
        </div>

        <div className="admin-form-actions">
          <div>
            {error ? (
              <p className="admin-status admin-status--error" role="alert">
                {error}
              </p>
            ) : null}
            {message ? (
              <p className="admin-status admin-status--success" role="status">
                {message}
              </p>
            ) : null}
          </div>
          <button className="button button--primary" disabled={saving} type="submit">
            {saving ? 'Saving...' : 'Save profile'}
          </button>
        </div>
      </form>
    </section>
  )
}
