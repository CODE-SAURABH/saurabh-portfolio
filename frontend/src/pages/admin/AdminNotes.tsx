import axios from 'axios'
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { apiClient } from '../../lib/apiClient'
import type { ApiData, ApiErrorBody } from '../../types/api'
import type { AdminNote, NoteFormValues } from '../../types/note'

function emptyNoteForm(): NoteFormValues {
  return {
    title: '',
    slug: '',
    topic_label: '',
    category: '',
    body: '',
    is_published: false,
    published_at: '',
  }
}

function toLocalInput(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const pad = (part: number) => String(part).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function fromLocalInput(value: string): string | null {
  if (!value) return null
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? null : date.toISOString()
}

function toNoteForm(note: AdminNote): NoteFormValues {
  return {
    title: note.title,
    slug: note.slug,
    topic_label: note.topic_label ?? '',
    category: note.category ?? '',
    body: note.body ?? '',
    is_published: note.is_published,
    published_at: note.published_at ? toLocalInput(note.published_at) : '',
  }
}

function nullable(value: string): string | null {
  const trimmed = value.trim()
  return trimmed ? trimmed : null
}

function slugify(value: string): string {
  return value
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 150)
}

function sortNotes(items: AdminNote[]): AdminNote[] {
  return [...items].sort((left, right) => {
    const leftDate = left.published_at ? new Date(left.published_at).getTime() : 0
    const rightDate = right.published_at ? new Date(right.published_at).getTime() : 0
    return rightDate - leftDate || right.created_at.localeCompare(left.created_at)
  })
}

function formatDate(value: string | null): string {
  if (!value) return 'No publish date'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'No publish date'
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function requestError(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as ApiErrorBody | undefined
    return body?.error?.message ?? fallback
  }
  return fallback
}

export default function AdminNotes() {
  const [notes, setNotes] = useState<AdminNote[]>([])
  const [form, setForm] = useState<NoteFormValues>(emptyNoteForm())
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [slugTouched, setSlugTouched] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [busyId, setBusyId] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    apiClient
      .get<ApiData<AdminNote[]>>('/admin/notes')
      .then((response) => {
        if (!active) return
        setNotes(sortNotes(response.data.data))
      })
      .catch((loadError: unknown) => {
        if (!active) return
        setError(requestError(loadError, 'The notes could not be loaded.'))
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  function updateField<K extends keyof NoteFormValues>(field: K, value: NoteFormValues[K]) {
    setForm((current) => ({ ...current, [field]: value }))
    setMessage(null)
  }

  const applyNote = (updated: AdminNote) => {
    setNotes((current) => {
      const exists = current.some((note) => note.id === updated.id)
      const next = exists
        ? current.map((note) => (note.id === updated.id ? updated : note))
        : [...current, updated]
      return sortNotes(next)
    })
  }

  const openCreate = () => {
    setForm(emptyNoteForm())
    setEditingId(null)
    setFormOpen(true)
    setSlugTouched(false)
    setError(null)
    setMessage(null)
  }

  const openEdit = (note: AdminNote) => {
    setForm(toNoteForm(note))
    setEditingId(note.id)
    setFormOpen(true)
    setSlugTouched(true)
    setError(null)
    setMessage(null)
  }

  const closeForm = () => {
    setFormOpen(false)
    setEditingId(null)
    setError(null)
  }

  const handleTitleChange = (value: string) => {
    setForm((current) => {
      const next = { ...current, title: value }
      if (!editingId && !slugTouched) {
        next.slug = slugify(value)
      }
      return next
    })
    setMessage(null)
  }

  const handleSlugChange = (value: string) => {
    setSlugTouched(true)
    updateField('slug', value)
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSaving(true)
    setError(null)
    setMessage(null)

    const payload = {
      title: form.title.trim(),
      slug: form.slug.trim(),
      topic_label: nullable(form.topic_label),
      category: nullable(form.category),
      body: nullable(form.body),
      is_published: form.is_published,
      published_at: fromLocalInput(form.published_at),
    }

    try {
      const response = editingId
        ? await apiClient.patch<ApiData<AdminNote>>(`/admin/notes/${editingId}`, payload)
        : await apiClient.post<ApiData<AdminNote>>('/admin/notes', payload)
      applyNote(response.data.data)
      setForm(toNoteForm(response.data.data))
      setSlugTouched(true)
      setFormOpen(false)
      setEditingId(null)
      setMessage(editingId ? 'Note saved.' : 'Note created.')
    } catch (saveError) {
      setError(requestError(saveError, 'The note could not be saved.'))
    } finally {
      setSaving(false)
    }
  }

  const togglePublished = async (note: AdminNote) => {
    setBusyId(note.id)
    setError(null)
    setMessage(null)
    try {
      const response = await apiClient.patch<ApiData<AdminNote>>(
        `/admin/notes/${note.id}/publish`,
        { value: !note.is_published },
      )
      applyNote(response.data.data)
      if (editingId === note.id) {
        setForm(toNoteForm(response.data.data))
      }
      setMessage(response.data.data.is_published ? 'Note published.' : 'Note unpublished.')
    } catch (toggleError) {
      setError(requestError(toggleError, 'The note could not be updated.'))
    } finally {
      setBusyId(null)
    }
  }

  const deleteNote = async (note: AdminNote) => {
    const confirmed = window.confirm(`Delete "${note.title}"?`)
    if (!confirmed) return

    setDeletingId(note.id)
    setError(null)
    setMessage(null)

    try {
      await apiClient.delete(`/admin/notes/${note.id}`)
      setNotes((current) => current.filter((entry) => entry.id !== note.id))
      if (editingId === note.id) {
        closeForm()
      }
      setMessage('Note deleted.')
    } catch (deleteError) {
      setError(requestError(deleteError, 'The note could not be deleted.'))
    } finally {
      setDeletingId(null)
    }
  }

  if (loading) {
    return <p className="admin-loading">Loading notes...</p>
  }

  return (
    <section className="admin-page">
      <div className="admin-page-head admin-page-head--row">
        <div>
          <p className="admin-kicker">Lab notes</p>
          <h1>
            Thinking in <span className="accent">public.</span>
          </h1>
          <p className="admin-page-lede">
            Short engineering notes, experiments, and observations. Publish only what is ready.
          </p>
        </div>
        <div className="admin-page-actions">
          <Link className="button button--small" to="/">
            Preview site
          </Link>
          <button className="button button--small button--primary" onClick={openCreate} type="button">
            Add note
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
              <p className="admin-form-label">{editingId ? 'Edit note' : 'New note'}</p>
              <p className="admin-form-hint">The label, address, and publish state.</p>
            </div>
            <div className="form-grid">
              <label className="field">
                <span>Title</span>
                <input
                  maxLength={300}
                  onChange={(event) => handleTitleChange(event.target.value)}
                  required
                  value={form.title}
                />
              </label>
              <label className="field">
                <span>Slug</span>
                <input
                  maxLength={150}
                  onChange={(event) => handleSlugChange(event.target.value)}
                  pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
                  required
                  value={form.slug}
                />
              </label>
              <label className="field">
                <span>Topic label</span>
                <input
                  maxLength={100}
                  onChange={(event) => updateField('topic_label', event.target.value)}
                  placeholder="AI SYSTEMS / 001"
                  value={form.topic_label}
                />
              </label>
              <label className="field">
                <span>Category</span>
                <input
                  maxLength={50}
                  onChange={(event) => updateField('category', event.target.value)}
                  placeholder="ai-systems"
                  value={form.category}
                />
              </label>
              <label className="field">
                <span>Published at</span>
                <input
                  onChange={(event) => updateField('published_at', event.target.value)}
                  type="datetime-local"
                  value={form.published_at}
                />
              </label>
              <label className="field field--check">
                <input
                  checked={form.is_published}
                  onChange={(event) => updateField('is_published', event.target.checked)}
                  type="checkbox"
                />
                <span>Published</span>
              </label>
            </div>
          </div>

          <div className="admin-form-section">
            <div>
              <p className="admin-form-label">Body</p>
              <p className="admin-form-hint">Plain text. Line breaks are preserved on the site.</p>
            </div>
            <div className="form-grid">
              <label className="field field--full">
                <span>Note body</span>
                <textarea
                  onChange={(event) => updateField('body', event.target.value)}
                  rows={10}
                  value={form.body}
                />
              </label>
            </div>
          </div>

          <div className="admin-form-actions">
            <p className="admin-form-hint">
              Published notes appear in the public lab feed immediately.
            </p>
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
                {saving ? 'Saving...' : editingId ? 'Save note' : 'Create note'}
              </button>
            </div>
          </div>
        </form>
      ) : null}

      <div className="admin-list-head">
        <p className="admin-form-label">
          {notes.length} {notes.length === 1 ? 'note' : 'notes'}
        </p>
        {notes.length > 0 ? <p className="admin-form-hint">Newest published notes appear first.</p> : null}
      </div>

      {notes.length === 0 && !formOpen ? (
        <div className="admin-empty">
          <p className="admin-form-label">No notes yet</p>
          <p>Add the first note to start the lab feed.</p>
          <button className="button button--small" onClick={openCreate} type="button">
            Add note
          </button>
        </div>
      ) : notes.length > 0 ? (
        <div className="admin-list">
          {notes.map((note, index) => (
            <article className="admin-entry" key={note.id}>
              <div className="admin-entry-order">
                <span className="admin-entry-index">{String(index + 1).padStart(2, '0')}</span>
              </div>

              <div className="admin-entry-body">
                <div className="admin-entry-head">
                  <div>
                    <h2>{note.title}</h2>
                    <p className="admin-entry-company">/{note.slug}</p>
                  </div>
                  <span
                    className={`admin-entry-badge${note.is_published ? '' : ' admin-entry-badge--muted'}`}
                  >
                    {note.is_published ? 'Published' : 'Draft'}
                  </span>
                </div>
                <p className="admin-entry-meta">
                  {note.topic_label ?? note.category ?? 'Uncategorized'} · {formatDate(note.published_at)}
                </p>
                {note.body ? (
                  <p className="admin-entry-description admin-note-body">{note.body}</p>
                ) : null}
              </div>

              <div className="admin-entry-actions">
                <button className="admin-inline-button" onClick={() => openEdit(note)} type="button">
                  Edit
                </button>
                <button
                  className="admin-inline-button"
                  disabled={busyId === note.id || deletingId === note.id}
                  onClick={() => togglePublished(note)}
                  type="button"
                >
                  {note.is_published ? 'Unpublish' : 'Publish'}
                </button>
                <button
                  className="admin-inline-button admin-inline-button--danger"
                  disabled={busyId === note.id || deletingId === note.id}
                  onClick={() => deleteNote(note)}
                  type="button"
                >
                  {deletingId === note.id ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  )
}
