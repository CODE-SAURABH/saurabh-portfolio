import type { ReactNode } from 'react'
import { ButtonLink } from '../components/ui/ButtonLink'

interface StubPageProps {
  eyebrow: string
  title: ReactNode
  lede: string
}

export function StubPage({ eyebrow, title, lede }: StubPageProps) {
  return (
    <section className="page-head">
      <div className="container">
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p className="page-lede">{lede}</p>
        <div className="placeholder">
          <span className="card-label">In progress / next milestone</span>
          <p>
            This route is wired and ready. The full content for this page is scheduled for the next
            build pass.
          </p>
          <ButtonLink to="/">Back home</ButtonLink>
        </div>
      </div>
    </section>
  )
}

export function NotFoundPage() {
  return (
    <section className="page-head">
      <div className="container">
        <p className="eyebrow">404 / Off the map</p>
        <h1>
          This page doesn&apos;t exist<span className="accent">.</span>
        </h1>
        <p className="page-lede">
          The link may be outdated, or the page may still be in progress. The work is a good place
          to pick up the trail.
        </p>
        <div className="not-found-actions">
          <ButtonLink to="/" variant="primary">
            Back home
          </ButtonLink>
          <ButtonLink to="/projects">Explore the work</ButtonLink>
        </div>
      </div>
    </section>
  )
}
