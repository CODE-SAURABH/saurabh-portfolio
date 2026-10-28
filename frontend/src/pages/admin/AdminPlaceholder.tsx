interface AdminPlaceholderProps {
  title: string
  description: string
}

export default function AdminPlaceholder({ title, description }: AdminPlaceholderProps) {
  return (
    <section className="admin-page">
      <div className="admin-page-head">
        <p className="admin-kicker">Next milestone</p>
        <h1>{title}</h1>
        <p className="admin-page-lede">{description}</p>
      </div>
      <div className="admin-placeholder">
        <p className="admin-form-label">Queued</p>
        <p>
          The API and editor for this section are next. Profile editing is live now, so start there
          while this screen is being built.
        </p>
      </div>
    </section>
  )
}
