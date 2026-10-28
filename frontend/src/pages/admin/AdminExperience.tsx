import axios from 'axios'
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { apiClient } from '../../lib/apiClient'
import type { ApiData, ApiErrorBody } from '../../types/api'
import type { Experience, ExperienceFormValues } from '../../types/experience'

function emptyForm(displayOrder: number): ExperienceFormValues {
  return {
    company: '',
    role_title: '',
    employment_type: '',
    start_date: '',
    end_date: '',
    is_current: false,
    description: '',
    display_order: displayOrder,
  }
}

function toForm(experience: Experience): ExperienceFormValues {
  return {
    company: experience.company,
    role_title: experience.role_title,
    employment_type: experience.employment_type ?? '',
    start_date: experience.start_date,
    end_date: experience.end_date ?? '',
    is_current: experience.is_current,
    description: experience.description ?? '',
    display_order: experience.display_order,
  }
}

function nullable(value: string): string | null {
  const trimmed = value.trim()
  return trimmed ? trimmed : null
}

function sortExperiences(items: Experience[]): Experience[] {
  return [...items].sort(
    (left, right) =>
      left.display_order - right.display_order || right.start_date.localeCompare(left.start_date),
  )
}

function formatDate(value: string): string {
  const date = new Date(`${value}T00:00:00`)
  if (Number.isNaN(date.getTime())) return value
  return new Intl.DateTimeFormat('en', { month: 'short', year: 'numeric' }).format(date)
}

function formatRange(experience: Experience): string {
  const start = formatDate(experience.start_date)
  if (experience.is_current) return `${start} — Present`
  if (experience.end_date) return `${start} — ${formatDate(experience.end_date)}`
  return start
}

function requestError(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as ApiErrorBody | undefined
    return body?.error?.message ?? fallback
  }
  return fallback
}

export default function AdminExperience() {
  const [experiences, setExperiences] = useState<Experience[]>([])
  const [form, setForm] = useState<ExperienceFormValues>(emptyForm(0))
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [reordering, setReordering] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    apiClient
      .get<ApiData<Experience[]>>('/admin/experience')
      .then((response) => {
        if (!active) return
        setExperiences(sortExperiences(response.data.data))
      })
      .catch((loadError: unknown) => {
        if (!active) return
        setError(requestError(loadError, 'The experience entries could not be loaded.'))
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  function updateField<K extends keyof ExperienceFormValues>(
    field: K,
    value: ExperienceFormValues[K],
  ) {
    setForm((current) => ({ ...current, [field]: value }))
    setMessage(null)
  }

  const openCreate = () => {
    const nextOrder =
      experiences.length > 0
        ? Math.max(...experiences.map((experience) => experience.display_order)) + 1
        : 0
    setForm(emptyForm(nextOrder))
    setEditingId(null)
    setFormOpen(true)
    setError(null)
    setMessage(null)
  }

  const openEdit = (experience: Experience) => {
    setForm(toForm(experience))
    setEditingId(experience.id)
    setFormOpen(true)
    setError(null)
    setMessage(null)
  }

  const closeForm = () => {
    setFormOpen(false)
    setEditingId(null)
    setError(null)
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError(null)
    setMessage(null)

    const payload = {
      company: form.company.trim(),
      role_title: form.role_title.trim(),
      employment_type: nullable(form.employment_type),
      start_date: form.start_date,
      end_date: form.is_current ? null : nullable(form.end_date),
      is_current: form.is_current,
      description: nullable(form.description),
      display_order: form.display_order,
    }

    try {
      if (editingId) {
        const response = await apiClient.patch<ApiData<Experience>>(
          `/admin/experience/${editingId}`,
          payload,
        )
        setExperiences((current) =>
          sortExperiences(
            current.map((experience) =>
              experience.id === editingId ? response.data.data : experience,
            ),
          ),
        )
        setMessage('Experience entry saved.')
      } else {
        const response = await apiClient.post<ApiData<Experience>>('/admin/experience', payload)
        setExperiences((current) => sortExperiences([...current, response.data.data]))
        setMessage('Experience entry added.')
      }
      setFormOpen(false)
      setEditingId(null)
    } catch (saveError) {
      setError(requestError(saveError, 'The experience entry could not be saved.'))
    } finally {
      setSaving(false)
    }
  }

  const moveEntry = async (index: number, direction: -1 | 1) => {
    const target = index + direction
    if (target < 0 || target >= experiences.length || reordering) return

    const reordered = [...experiences]
    const [moved] = reordered.splice(index, 1)
    reordered.splice(target, 0, moved)
    const items = reordered.map((experience, order) => ({
      id: experience.id,
      display_order: order,
    }))

    setReordering(true)
    setError(null)
    setMessage(null)

    try {
      const response = await apiClient.patch<ApiData<Experience[]>>(
        '/admin/experience/reorder',
        { items },
      )
      setExperiences(sortExperiences(response.data.data))
      setMessage('Display order updated.')
    } catch (reorderError) {
      setError(requestError(reorderError, 'The display order could not be updated.'))
    } finally {
      setReordering(false)
    }
  }

  const deleteEntry = async (experience: Experience) => {
    const confirmed = window.confirm(
      `Delete "${experience.role_title}" at ${experience.company}? This cannot be undone.`,
    )
    if (!confirmed) return

    setDeletingId(experience.id)
    setError(null)
    setMessage(null)

    try {
      await apiClient.delete(`/admin/experience/${experience.id}`)
      setExperiences((current) =>
        current.filter((entry) => entry.id !== experience.id),
      )
      if (editingId === experience.id) {
        setFormOpen(false)
        setEditingId(null)
      }
      setMessage('Experience entry deleted.')
    } catch (deleteError) {
      setError(requestError(deleteError, 'The experience entry could not be deleted.'))
    } finally {
      setDeletingId(null)
    }
  }

  if (loading) {
    return <p className="admin-loading">Loading experience...</p>
  }

  return (
    <section className="admin-page">
      <div className="admin-page-head admin-page-head--row">
        <div>
          <p className="admin-kicker">Experience</p>
          <h1>
            The work, in <span className="accent">sequence.</span>
          </h1>
          <p className="admin-page-lede">
            Add roles, set the timeline, and choose how they appear on the experience page.
          </p>
        </div>
        <div className="admin-page-actions">
          <Link className="button button--small" to="/">
            Preview site
          </Link>
          <button className="button button--small button--primary" onClick={openCreate} type="button">
            Add experience
          </button>
        </div>
      </div>

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

      {formOpen ? (
        <form className="admin-form admin-form--spaced" onSubmit={handleSubmit}>
          <div className="admin-form-section">
            <div>
              <p className="admin-form-label">{editingId ? 'Edit role' : 'New role'}</p>
              <p className="admin-form-hint">The details visitors see on the experience page.</p>
            </div>
            <div className="form-grid">
              <label className="field">
                <span>Company</span>
                <input
                  maxLength={200}
                  onChange={(event) => updateField('company', event.target.value)}
                  required
                  value={form.company}
                />
              </label>
              <label className="field">
                <span>Role title</span>
                <input
                  maxLength={200}
                  onChange={(event) => updateField('role_title', event.target.value)}
                  required
                  value={form.role_title}
                />
              </label>
              <label className="field">
                <span>Employment type</span>
                <input
                  maxLength={50}
                  onChange={(event) => updateField('employment_type', event.target.value)}
                  placeholder="Full-time"
                  value={form.employment_type}
                />
              </label>
              <label className="field">
                <span>Display order</span>
                <input
                  min={0}
                  onChange={(event) =>
                    updateField('display_order', Number(event.target.value) || 0)
                  }
                  type="number"
                  value={form.display_order}
                />
              </label>
            </div>
          </div>

          <div className="admin-form-section">
            <div>
              <p className="admin-form-label">Timeline</p>
              <p className="admin-form-hint">Current roles hide the end date.</p>
            </div>
            <div className="form-grid">
              <label className="field">
                <span>Start date</span>
                <input
                  onChange={(event) => updateField('start_date', event.target.value)}
                  required
                  type="date"
                  value={form.start_date}
                />
              </label>
              <label className="field">
                <span>End date</span>
                <input
                  disabled={form.is_current}
                  onChange={(event) => updateField('end_date', event.target.value)}
                  type="date"
                  value={form.end_date}
                />
              </label>
              <label className="field field--check field--full">
                <input
                  checked={form.is_current}
                  onChange={(event) => {
                    const checked = event.target.checked
                    setForm((current) => ({
                      ...current,
                      is_current: checked,
                      end_date: checked ? '' : current.end_date,
                    }))
                    setMessage(null)
                  }}
                  type="checkbox"
                />
                <span>This is my current role</span>
              </label>
              <label className="field field--full">
                <span>Description</span>
                <textarea
                  onChange={(event) => updateField('description', event.target.value)}
                  rows={5}
                  value={form.description}
                />
              </label>
            </div>
          </div>

          <div className="admin-form-actions">
            <p className="admin-form-hint">Changes appear on the public site after saving.</p>
            <div className="admin-form-buttons">
              <button
                className="button button--small"
                disabled={saving}
                onClick={closeForm}
                type="button"
              >
                Cancel
              </button>
              <button className="button button--small button--primary" disabled={saving} type="submit">
                {saving ? 'Saving...' : editingId ? 'Save changes' : 'Add experience'}
              </button>
            </div>
          </div>
        </form>
      ) : null}

      <div className="admin-list-head">
        <p className="admin-form-label">
          {experiences.length} {experiences.length === 1 ? 'role' : 'roles'}
        </p>
        {experiences.length > 0 ? (
          <p className="admin-form-hint">Use the arrows to change the order.</p>
        ) : null}
      </div>

      {experiences.length === 0 && !formOpen ? (
        <div className="admin-empty">
          <p className="admin-form-label">No roles yet</p>
          <p>Add the first experience entry to start building the timeline.</p>
          <button className="button button--small" onClick={openCreate} type="button">
            Add experience
          </button>
        </div>
      ) : experiences.length > 0 ? (
        <div className="admin-list">
          {experiences.map((experience, index) => (
            <article className="admin-entry" key={experience.id}>
              <div className="admin-entry-order" aria-label="Display order controls">
                <button
                  aria-label={`Move ${experience.company} up`}
                  className="admin-order-button"
                  disabled={index === 0 || reordering}
                  onClick={() => moveEntry(index, -1)}
                  type="button"
                >
                  ↑
                </button>
                <span className="admin-entry-index">
                  {String(index + 1).padStart(2, '0')}
                </span>
                <button
                  aria-label={`Move ${experience.company} down`}
                  className="admin-order-button"
                  disabled={index === experiences.length - 1 || reordering}
                  onClick={() => moveEntry(index, 1)}
                  type="button"
                >
                  ↓
                </button>
              </div>

              <div className="admin-entry-body">
                <div className="admin-entry-head">
                  <div>
                    <h2>{experience.role_title}</h2>
                    <p className="admin-entry-company">{experience.company}</p>
                  </div>
                  {experience.is_current ? (
                    <span className="admin-entry-badge">Current</span>
                  ) : null}
                </div>
                <p className="admin-entry-meta">
                  {formatRange(experience)}
                  {experience.employment_type ? ` · ${experience.employment_type}` : ''}
                </p>
                {experience.description ? (
                  <p className="admin-entry-description">{experience.description}</p>
                ) : null}
              </div>

              <div className="admin-entry-actions">
                <button
                  className="admin-inline-button"
                  onClick={() => openEdit(experience)}
                  type="button"
                >
                  Edit
                </button>
                <button
                  className="admin-inline-button admin-inline-button--danger"
                  disabled={deletingId === experience.id}
                  onClick={() => deleteEntry(experience)}
                  type="button"
                >
                  {deletingId === experience.id ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  )
}
