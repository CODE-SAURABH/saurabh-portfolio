import { Link } from 'react-router-dom'

const sections = [
  {
    title: 'Profile',
    description: 'Name, headline, biography, links, and availability.',
    to: '/change-data/profile',
    status: 'Ready',
  },
  {
    title: 'Experience',
    description: 'Roles, dates, and the story of each position.',
    to: '/change-data/experience',
    status: 'Ready',
  },
  {
    title: 'Projects',
    description: 'Case studies, technologies, sections, and publishing.',
    to: '/change-data/projects',
    status: 'Ready',
  },
  {
    title: 'Lab notes',
    description: 'Short engineering notes and experiments.',
    to: '/change-data/lab',
    status: 'Ready',
  },
]

export default function AdminDashboard() {
  return (
    <section className="admin-page">
      <div className="admin-page-head">
        <p className="admin-kicker">Overview</p>
        <h1>
          Edit once. Update <span className="accent">everywhere.</span>
        </h1>
        <p className="admin-page-lede">
          This workspace is the source of truth for the public portfolio. Start with the profile,
          then work through the content sections.
        </p>
      </div>

      <div className="admin-grid">
        {sections.map((section) => (
          <Link className="admin-card" key={section.title} to={section.to}>
            <span className="admin-card-status">{section.status}</span>
            <h2>{section.title}</h2>
            <p>{section.description}</p>
            <span className="admin-card-arrow" aria-hidden="true">
              &rarr;
            </span>
          </Link>
        ))}
      </div>
    </section>
  )
}
