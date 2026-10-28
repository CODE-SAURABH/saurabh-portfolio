import axios from 'axios'
import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { apiClient } from '../../lib/apiClient'
import type { ApiData, ApiErrorBody } from '../../types/api'
import type {
  AdminProject,
  AdminProjectListItem,
  AdminProjectSection,
  ProjectCategory,
  ProjectFormValues,
  ProjectSectionFormValues,
  ProjectVisualVariant,
} from '../../types/project'

const categoryOptions: { value: ProjectCategory; label: string }[] = [
  { value: 'ai', label: 'AI systems' },
  { value: 'vision', label: 'Computer vision' },
  { value: 'tools', label: 'Developer tools' },
  { value: 'product', label: 'Product concepts' },
]

const visualOptions: { value: ProjectVisualVariant; label: string }[] = [
  { value: 'rag', label: 'RAG' },
  { value: 'vision', label: 'Vision' },
  { value: 'nodes', label: 'Nodes' },
  { value: 'journal', label: 'Journal' },
  { value: 'utility', label: 'Utility' },
]

function emptyProjectForm(displayOrder: number): ProjectFormValues {
  return {
    title: '',
    slug: '',
    short_description: '',
    long_description: '',
    status: '',
    category: 'ai',
    visual_type: 'rag',
    is_published: false,
    is_featured: false,
    display_order: displayOrder,
    github_url: '',
    live_url: '',
    thumbnail_url: '',
  }
}

function emptySectionForm(displayOrder: number): ProjectSectionFormValues {
  return {
    overline: '',
    title: '',
    body: '',
    display_order: displayOrder,
  }
}

function toProjectForm(project: AdminProject): ProjectFormValues {
  return {
    title: project.title,
    slug: project.slug,
    short_description: project.short_description ?? '',
    long_description: project.long_description ?? '',
    status: project.status ?? '',
    category: project.category,
    visual_type: project.visual_type ?? '',
    is_published: project.is_published,
    is_featured: project.is_featured,
    display_order: project.display_order,
    github_url: project.github_url ?? '',
    live_url: project.live_url ?? '',
    thumbnail_url: project.thumbnail_url ?? '',
  }
}

function toSectionForm(section: AdminProjectSection): ProjectSectionFormValues {
  return {
    overline: section.overline ?? '',
    title: section.title,
    body: section.body ?? '',
    display_order: section.display_order,
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
    .slice(0, 100)
}

function sortProjects(items: AdminProjectListItem[]): AdminProjectListItem[] {
  return [...items].sort(
    (left, right) =>
      left.display_order - right.display_order || left.created_at.localeCompare(right.created_at),
  )
}

function sortSections(items: AdminProjectSection[]): AdminProjectSection[] {
  return [...items].sort((left, right) => left.display_order - right.display_order)
}

function categoryLabel(category: ProjectCategory): string {
  return categoryOptions.find((option) => option.value === category)?.label ?? category
}

function requestError(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as ApiErrorBody | undefined
    return body?.error?.message ?? fallback
  }
  return fallback
}

export default function AdminProjects() {
  const [projects, setProjects] = useState<AdminProjectListItem[]>([])
  const [selected, setSelected] = useState<AdminProject | null>(null)
  const [form, setForm] = useState<ProjectFormValues>(emptyProjectForm(0))
  const [editingId, setEditingId] = useState<string | null>(null)
  const [formOpen, setFormOpen] = useState(false)
  const [slugTouched, setSlugTouched] = useState(false)
  const [loading, setLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [reordering, setReordering] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [technologyName, setTechnologyName] = useState('')
  const [technologyBusy, setTechnologyBusy] = useState(false)
  const [sectionForm, setSectionForm] = useState<ProjectSectionFormValues>(emptySectionForm(0))
  const [sectionEditingId, setSectionEditingId] = useState<string | null>(null)
  const [sectionFormOpen, setSectionFormOpen] = useState(false)
  const [sectionSaving, setSectionSaving] = useState(false)
  const [sectionDeletingId, setSectionDeletingId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    apiClient
      .get<ApiData<AdminProjectListItem[]>>('/admin/projects')
      .then((response) => {
        if (!active) return
        setProjects(sortProjects(response.data.data))
      })
      .catch((loadError: unknown) => {
        if (!active) return
        setError(requestError(loadError, 'The projects could not be loaded.'))
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  function updateField<K extends keyof ProjectFormValues>(
    field: K,
    value: ProjectFormValues[K],
  ) {
    setForm((current) => ({ ...current, [field]: value }))
    setMessage(null)
  }

  function updateSectionField<K extends keyof ProjectSectionFormValues>(
    field: K,
    value: ProjectSectionFormValues[K],
  ) {
    setSectionForm((current) => ({ ...current, [field]: value }))
    setMessage(null)
  }

  const applySelected = (updated: AdminProject) => {
    setSelected(updated)
    setProjects((current) => {
      const exists = current.some((project) => project.id === updated.id)
      const next = exists
        ? current.map((project) => (project.id === updated.id ? updated : project))
        : [...current, updated]
      return sortProjects(next)
    })
  }

  const applyFlagUpdate = (updated: AdminProject) => {
    setProjects((current) =>
      sortProjects(
        current.map((project) => (project.id === updated.id ? updated : project)),
      ),
    )
    setSelected((current) => (current?.id === updated.id ? updated : current))
    setForm((current) => (editingId === updated.id ? toProjectForm(updated) : current))
  }

  const closeSectionForm = () => {
    setSectionFormOpen(false)
    setSectionEditingId(null)
  }

  const openCreate = () => {
    const nextOrder =
      projects.length > 0
        ? Math.max(...projects.map((project) => project.display_order)) + 1
        : 0
    setForm(emptyProjectForm(nextOrder))
    setEditingId(null)
    setSelected(null)
    setFormOpen(true)
    setSlugTouched(false)
    closeSectionForm()
    setError(null)
    setMessage(null)
  }

  const openEdit = async (project: AdminProjectListItem) => {
    setDetailLoading(true)
    setError(null)
    setMessage(null)
    closeSectionForm()

    try {
      const response = await apiClient.get<ApiData<AdminProject>>(
        `/admin/projects/${project.id}`,
      )
      setSelected(response.data.data)
      setForm(toProjectForm(response.data.data))
      setEditingId(project.id)
      setFormOpen(true)
      setSlugTouched(true)
    } catch (loadError) {
      setError(requestError(loadError, 'The project could not be loaded.'))
    } finally {
      setDetailLoading(false)
    }
  }

  const closeProjectForm = () => {
    setFormOpen(false)
    setEditingId(null)
    setError(null)
  }

  const closeSelected = () => {
    setSelected(null)
    setFormOpen(false)
    setEditingId(null)
    closeSectionForm()
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
      short_description: nullable(form.short_description),
      long_description: nullable(form.long_description),
      status: nullable(form.status),
      category: form.category,
      visual_type: form.visual_type || null,
      is_published: form.is_published,
      is_featured: form.is_featured,
      display_order: form.display_order,
      github_url: nullable(form.github_url),
      live_url: nullable(form.live_url),
      thumbnail_url: nullable(form.thumbnail_url),
    }

    try {
      const response = editingId
        ? await apiClient.patch<ApiData<AdminProject>>(
            `/admin/projects/${editingId}`,
            payload,
          )
        : await apiClient.post<ApiData<AdminProject>>('/admin/projects', payload)
      applySelected(response.data.data)
      setForm(toProjectForm(response.data.data))
      setSlugTouched(true)
      setFormOpen(false)
      setEditingId(null)
      setMessage(editingId ? 'Project saved.' : 'Project created.')
    } catch (saveError) {
      setError(requestError(saveError, 'The project could not be saved.'))
    } finally {
      setSaving(false)
    }
  }

  const moveProject = async (index: number, direction: -1 | 1) => {
    const target = index + direction
    if (target < 0 || target >= projects.length || reordering) return

    const reordered = [...projects]
    const [moved] = reordered.splice(index, 1)
    reordered.splice(target, 0, moved)
    const items = reordered.map((project, order) => ({
      id: project.id,
      display_order: order,
    }))

    setReordering(true)
    setError(null)
    setMessage(null)

    try {
      const response = await apiClient.patch<ApiData<AdminProjectListItem[]>>(
        '/admin/projects/reorder',
        { items },
      )
      setProjects(sortProjects(response.data.data))
      setMessage('Project order updated.')
    } catch (reorderError) {
      setError(requestError(reorderError, 'The project order could not be updated.'))
    } finally {
      setReordering(false)
    }
  }

  const togglePublished = async (project: AdminProjectListItem) => {
    setError(null)
    setMessage(null)
    try {
      const response = await apiClient.patch<ApiData<AdminProject>>(
        `/admin/projects/${project.id}/publish`,
        { value: !project.is_published },
      )
      applyFlagUpdate(response.data.data)
      setMessage(response.data.data.is_published ? 'Project published.' : 'Project unpublished.')
    } catch (toggleError) {
      setError(requestError(toggleError, 'The project could not be updated.'))
    }
  }

  const toggleFeatured = async (project: AdminProjectListItem) => {
    setError(null)
    setMessage(null)
    try {
      const response = await apiClient.patch<ApiData<AdminProject>>(
        `/admin/projects/${project.id}/feature`,
        { value: !project.is_featured },
      )
      applyFlagUpdate(response.data.data)
      setMessage(response.data.data.is_featured ? 'Project featured.' : 'Project unfeatured.')
    } catch (toggleError) {
      setError(requestError(toggleError, 'The project could not be updated.'))
    }
  }

  const deleteProject = async (project: AdminProjectListItem) => {
    const confirmed = window.confirm(
      `Delete "${project.title}"? This also removes its sections and technologies.`,
    )
    if (!confirmed) return

    setDeletingId(project.id)
    setError(null)
    setMessage(null)

    try {
      await apiClient.delete(`/admin/projects/${project.id}`)
      setProjects((current) => current.filter((entry) => entry.id !== project.id))
      if (selected?.id === project.id) {
        closeSelected()
      }
      if (editingId === project.id) {
        setFormOpen(false)
        setEditingId(null)
      }
      setMessage('Project deleted.')
    } catch (deleteError) {
      setError(requestError(deleteError, 'The project could not be deleted.'))
    } finally {
      setDeletingId(null)
    }
  }

  const handleAddTechnology = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!selected) return
    const name = technologyName.trim()
    if (!name) return

    setTechnologyBusy(true)
    setError(null)
    setMessage(null)

    try {
      const response = await apiClient.post<ApiData<AdminProject['technologies'][number]>>(
        `/admin/projects/${selected.id}/technologies`,
        { name, display_order: selected.technologies.length },
      )
      applySelected({
        ...selected,
        technologies: [...selected.technologies, response.data.data],
      })
      setTechnologyName('')
      setMessage('Technology added.')
    } catch (technologyError) {
      setError(requestError(technologyError, 'The technology could not be added.'))
    } finally {
      setTechnologyBusy(false)
    }
  }

  const removeTechnology = async (technologyId: string) => {
    if (!selected) return
    setTechnologyBusy(true)
    setError(null)
    setMessage(null)

    try {
      await apiClient.delete(
        `/admin/projects/${selected.id}/technologies/${technologyId}`,
      )
      applySelected({
        ...selected,
        technologies: selected.technologies.filter(
          (technology) => technology.id !== technologyId,
        ),
      })
      setMessage('Technology removed.')
    } catch (technologyError) {
      setError(requestError(technologyError, 'The technology could not be removed.'))
    } finally {
      setTechnologyBusy(false)
    }
  }

  const openSectionCreate = () => {
    if (!selected) return
    setSectionForm(emptySectionForm(selected.sections.length))
    setSectionEditingId(null)
    setSectionFormOpen(true)
    setError(null)
    setMessage(null)
  }

  const openSectionEdit = (section: AdminProjectSection) => {
    setSectionForm(toSectionForm(section))
    setSectionEditingId(section.id)
    setSectionFormOpen(true)
    setError(null)
    setMessage(null)
  }

  const handleSectionSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!selected) return

    setSectionSaving(true)
    setError(null)
    setMessage(null)

    const payload = {
      overline: nullable(sectionForm.overline),
      title: sectionForm.title.trim(),
      body: nullable(sectionForm.body),
      display_order: sectionForm.display_order,
    }

    try {
      const response = sectionEditingId
        ? await apiClient.patch<ApiData<AdminProjectSection>>(
            `/admin/projects/${selected.id}/sections/${sectionEditingId}`,
            payload,
          )
        : await apiClient.post<ApiData<AdminProjectSection>>(
            `/admin/projects/${selected.id}/sections`,
            payload,
          )
      const sections = sectionEditingId
        ? selected.sections.map((section) =>
            section.id === sectionEditingId ? response.data.data : section,
          )
        : [...selected.sections, response.data.data]
      applySelected({ ...selected, sections: sortSections(sections) })
      closeSectionForm()
      setMessage(sectionEditingId ? 'Section saved.' : 'Section added.')
    } catch (sectionError) {
      setError(requestError(sectionError, 'The section could not be saved.'))
    } finally {
      setSectionSaving(false)
    }
  }

  const deleteSection = async (section: AdminProjectSection) => {
    if (!selected) return
    const confirmed = window.confirm(`Delete the section "${section.title}"?`)
    if (!confirmed) return

    setSectionDeletingId(section.id)
    setError(null)
    setMessage(null)

    try {
      await apiClient.delete(
        `/admin/projects/${selected.id}/sections/${section.id}`,
      )
      applySelected({
        ...selected,
        sections: selected.sections.filter((entry) => entry.id !== section.id),
      })
      if (sectionEditingId === section.id) {
        closeSectionForm()
      }
      setMessage('Section deleted.')
    } catch (sectionError) {
      setError(requestError(sectionError, 'The section could not be deleted.'))
    } finally {
      setSectionDeletingId(null)
    }
  }

  if (loading) {
    return <p className="admin-loading">Loading projects...</p>
  }

  return (
    <section className="admin-page">
      <div className="admin-page-head admin-page-head--row">
        <div>
          <p className="admin-kicker">Projects</p>
          <h1>
            Work that <span className="accent">explains itself.</span>
          </h1>
          <p className="admin-page-lede">
            Publish case studies, attach technologies, and control what appears on the home page.
          </p>
        </div>
        <div className="admin-page-actions">
          <Link className="button button--small" to="/">
            Preview site
          </Link>
          <button className="button button--small button--primary" onClick={openCreate} type="button">
            Add project
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
      {detailLoading ? <p className="admin-loading">Loading project...</p> : null}

      {formOpen ? (
        <form className="admin-form admin-form--spaced" onSubmit={handleSubmit}>
          <div className="admin-form-section">
            <div>
              <p className="admin-form-label">{editingId ? 'Edit project' : 'New project'}</p>
              <p className="admin-form-hint">The identity and placement of the case study.</p>
            </div>
            <div className="form-grid">
              <label className="field">
                <span>Title</span>
                <input
                  maxLength={200}
                  onChange={(event) => handleTitleChange(event.target.value)}
                  required
                  value={form.title}
                />
              </label>
              <label className="field">
                <span>Slug</span>
                <input
                  maxLength={100}
                  onChange={(event) => handleSlugChange(event.target.value)}
                  pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
                  required
                  value={form.slug}
                />
              </label>
              <label className="field">
                <span>Category</span>
                <select
                  onChange={(event) =>
                    updateField('category', event.target.value as ProjectCategory)
                  }
                  value={form.category}
                >
                  {categoryOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Visual</span>
                <select
                  onChange={(event) =>
                    updateField(
                      'visual_type',
                      event.target.value as ProjectVisualVariant | '',
                    )
                  }
                  value={form.visual_type}
                >
                  <option value="">No visual</option>
                  {visualOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Status</span>
                <input
                  maxLength={50}
                  onChange={(event) => updateField('status', event.target.value)}
                  placeholder="Completed"
                  value={form.status}
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
              <p className="admin-form-label">Story</p>
              <p className="admin-form-hint">Short copy for cards; longer context for the case study.</p>
            </div>
            <div className="form-grid">
              <label className="field field--full">
                <span>Short description</span>
                <textarea
                  maxLength={400}
                  onChange={(event) => updateField('short_description', event.target.value)}
                  rows={3}
                  value={form.short_description}
                />
              </label>
              <label className="field field--full">
                <span>Long description</span>
                <textarea
                  onChange={(event) => updateField('long_description', event.target.value)}
                  rows={6}
                  value={form.long_description}
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
                <span>Live URL</span>
                <input
                  maxLength={500}
                  onChange={(event) => updateField('live_url', event.target.value)}
                  type="url"
                  value={form.live_url}
                />
              </label>
              <label className="field field--full">
                <span>Thumbnail URL</span>
                <input
                  maxLength={500}
                  onChange={(event) => updateField('thumbnail_url', event.target.value)}
                  type="url"
                  value={form.thumbnail_url}
                />
              </label>
            </div>
          </div>

          <div className="admin-form-section">
            <div>
              <p className="admin-form-label">Publishing</p>
              <p className="admin-form-hint">Only published projects appear on the public site.</p>
            </div>
            <div className="form-grid">
              <label className="field field--check field--full">
                <input
                  checked={form.is_published}
                  onChange={(event) => updateField('is_published', event.target.checked)}
                  type="checkbox"
                />
                <span>Published</span>
              </label>
              <label className="field field--check field--full">
                <input
                  checked={form.is_featured}
                  onChange={(event) => updateField('is_featured', event.target.checked)}
                  type="checkbox"
                />
                <span>Featured on the home page</span>
              </label>
            </div>
          </div>

          <div className="admin-form-actions">
            <p className="admin-form-hint">Changes appear on the public site after saving.</p>
            <div className="admin-form-buttons">
              <button
                className="button button--small"
                disabled={saving}
                onClick={closeProjectForm}
                type="button"
              >
                Cancel
              </button>
              <button className="button button--small button--primary" disabled={saving} type="submit">
                {saving ? 'Saving...' : editingId ? 'Save project' : 'Create project'}
              </button>
            </div>
          </div>
        </form>
      ) : null}

      {selected && !formOpen ? (
        <div className="admin-project-workspace">
          <div className="admin-project-workspace-head">
            <div>
              <p className="admin-form-label">Selected project</p>
              <h2>{selected.title}</h2>
              <p className="admin-entry-meta">
                /{selected.slug} · {categoryLabel(selected.category)}
                {selected.status ? ` · ${selected.status}` : ''}
              </p>
            </div>
            <div className="admin-form-buttons">
              <button
                className="button button--small"
                onClick={() => openEdit(selected)}
                type="button"
              >
                Edit details
              </button>
              <button className="button button--small" onClick={closeSelected} type="button">
                Close
              </button>
            </div>
          </div>

          <div className="admin-project-panels">
            <section className="admin-panel">
              <div className="admin-panel-head">
                <div>
                  <p className="admin-form-label">Technologies</p>
                  <p className="admin-form-hint">Short tags shown on cards and detail pages.</p>
                </div>
                <span className="admin-panel-count">{selected.technologies.length}</span>
              </div>

              <div className="admin-chip-list">
                {selected.technologies.length === 0 ? (
                  <p className="admin-empty-inline">No technologies yet.</p>
                ) : (
                  selected.technologies.map((technology) => (
                    <span className="admin-chip" key={technology.id}>
                      {technology.name}
                      <button
                        aria-label={`Remove ${technology.name}`}
                        disabled={technologyBusy}
                        onClick={() => removeTechnology(technology.id)}
                        type="button"
                      >
                        ×
                      </button>
                    </span>
                  ))
                )}
              </div>

              <form className="admin-inline-form" onSubmit={handleAddTechnology}>
                <input
                  aria-label="Technology name"
                  className="admin-inline-input"
                  maxLength={100}
                  onChange={(event) => setTechnologyName(event.target.value)}
                  placeholder="Add a technology"
                  value={technologyName}
                />
                <button
                  className="button button--small"
                  disabled={technologyBusy || !technologyName.trim()}
                  type="submit"
                >
                  {technologyBusy ? 'Saving...' : 'Add'}
                </button>
              </form>
            </section>

            <section className="admin-panel admin-panel--wide">
              <div className="admin-panel-head">
                <div>
                  <p className="admin-form-label">Case-study sections</p>
                  <p className="admin-form-hint">Ordered blocks for the project detail page.</p>
                </div>
                <button className="button button--small" onClick={openSectionCreate} type="button">
                  Add section
                </button>
              </div>

              {sectionFormOpen ? (
                <form className="admin-section-form" onSubmit={handleSectionSubmit}>
                  <div className="form-grid">
                    <label className="field">
                      <span>Overline</span>
                      <input
                        maxLength={100}
                        onChange={(event) => updateSectionField('overline', event.target.value)}
                        placeholder="01 / Problem"
                        value={sectionForm.overline}
                      />
                    </label>
                    <label className="field">
                      <span>Title</span>
                      <input
                        maxLength={200}
                        onChange={(event) => updateSectionField('title', event.target.value)}
                        required
                        value={sectionForm.title}
                      />
                    </label>
                    <label className="field">
                      <span>Display order</span>
                      <input
                        min={0}
                        onChange={(event) =>
                          updateSectionField(
                            'display_order',
                            Number(event.target.value) || 0,
                          )
                        }
                        type="number"
                        value={sectionForm.display_order}
                      />
                    </label>
                    <label className="field field--full">
                      <span>Body</span>
                      <textarea
                        onChange={(event) => updateSectionField('body', event.target.value)}
                        rows={5}
                        value={sectionForm.body}
                      />
                    </label>
                  </div>
                  <div className="admin-section-form-actions">
                    <button
                      className="button button--small"
                      disabled={sectionSaving}
                      onClick={closeSectionForm}
                      type="button"
                    >
                      Cancel
                    </button>
                    <button
                      className="button button--small button--primary"
                      disabled={sectionSaving}
                      type="submit"
                    >
                      {sectionSaving ? 'Saving...' : sectionEditingId ? 'Save section' : 'Add section'}
                    </button>
                  </div>
                </form>
              ) : null}

              {selected.sections.length === 0 ? (
                <p className="admin-empty-inline">No sections yet.</p>
              ) : (
                <div className="admin-section-list">
                  {selected.sections.map((section) => (
                    <article className="admin-section-item" key={section.id}>
                      <div>
                        {section.overline ? (
                          <p className="admin-form-label">{section.overline}</p>
                        ) : null}
                        <h3>{section.title}</h3>
                        {section.body ? <p>{section.body}</p> : null}
                      </div>
                      <div className="admin-section-actions">
                        <button
                          className="admin-inline-button"
                          onClick={() => openSectionEdit(section)}
                          type="button"
                        >
                          Edit
                        </button>
                        <button
                          className="admin-inline-button admin-inline-button--danger"
                          disabled={sectionDeletingId === section.id}
                          onClick={() => deleteSection(section)}
                          type="button"
                        >
                          {sectionDeletingId === section.id ? 'Deleting...' : 'Delete'}
                        </button>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </section>
          </div>
        </div>
      ) : null}

      <div className="admin-list-head">
        <p className="admin-form-label">
          {projects.length} {projects.length === 1 ? 'project' : 'projects'}
        </p>
        {projects.length > 0 ? (
          <p className="admin-form-hint">Use the arrows to change the order.</p>
        ) : null}
      </div>

      {projects.length === 0 && !formOpen ? (
        <div className="admin-empty">
          <p className="admin-form-label">No projects yet</p>
          <p>Add the first project to start building the work section.</p>
          <button className="button button--small" onClick={openCreate} type="button">
            Add project
          </button>
        </div>
      ) : projects.length > 0 ? (
        <div className="admin-list">
          {projects.map((project, index) => (
            <article
              className={`admin-project-card${selected?.id === project.id ? ' is-selected' : ''}`}
              key={project.id}
            >
              <div className="admin-entry-order" aria-label="Display order controls">
                <button
                  aria-label={`Move ${project.title} up`}
                  className="admin-order-button"
                  disabled={index === 0 || reordering}
                  onClick={() => moveProject(index, -1)}
                  type="button"
                >
                  ↑
                </button>
                <span className="admin-entry-index">
                  {String(index + 1).padStart(2, '0')}
                </span>
                <button
                  aria-label={`Move ${project.title} down`}
                  className="admin-order-button"
                  disabled={index === projects.length - 1 || reordering}
                  onClick={() => moveProject(index, 1)}
                  type="button"
                >
                  ↓
                </button>
              </div>

              <div className="admin-project-body">
                <div className="admin-project-head">
                  <div>
                    <h2>{project.title}</h2>
                    <p className="admin-entry-company">/{project.slug}</p>
                  </div>
                  <div className="admin-project-badges">
                    <span
                      className={`admin-entry-badge${project.is_published ? '' : ' admin-entry-badge--muted'}`}
                    >
                      {project.is_published ? 'Published' : 'Draft'}
                    </span>
                    {project.is_featured ? (
                      <span className="admin-entry-badge">Featured</span>
                    ) : null}
                  </div>
                </div>
                <p className="admin-entry-meta">
                  {categoryLabel(project.category)}
                  {project.status ? ` · ${project.status}` : ''} · {project.technologies.length}{' '}
                  technologies
                </p>
                {project.short_description ? (
                  <p className="admin-entry-description">{project.short_description}</p>
                ) : null}
                {project.technologies.length > 0 ? (
                  <div className="admin-chip-list admin-chip-list--compact">
                    {project.technologies.map((technology) => (
                      <span className="admin-chip admin-chip--static" key={technology.id}>
                        {technology.name}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>

              <div className="admin-project-actions">
                <button
                  className="admin-inline-button"
                  onClick={() => openEdit(project)}
                  type="button"
                >
                  Edit
                </button>
                <button
                  className="admin-inline-button"
                  onClick={() => togglePublished(project)}
                  type="button"
                >
                  {project.is_published ? 'Unpublish' : 'Publish'}
                </button>
                <button
                  className="admin-inline-button"
                  onClick={() => toggleFeatured(project)}
                  type="button"
                >
                  {project.is_featured ? 'Unfeature' : 'Feature'}
                </button>
                <button
                  className="admin-inline-button admin-inline-button--danger"
                  disabled={deletingId === project.id}
                  onClick={() => deleteProject(project)}
                  type="button"
                >
                  {deletingId === project.id ? 'Deleting...' : 'Delete'}
                </button>
              </div>
            </article>
          ))}
        </div>
      ) : null}
    </section>
  )
}
