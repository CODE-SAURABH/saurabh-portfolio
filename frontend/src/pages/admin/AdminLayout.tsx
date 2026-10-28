import { Link, NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../../features/admin/auth-context'

const adminNav = [
  { label: 'Overview', to: '/change-data', end: true },
  { label: 'Profile', to: '/change-data/profile' },
  { label: 'Experience', to: '/change-data/experience' },
  { label: 'Projects', to: '/change-data/projects' },
  { label: 'Lab notes', to: '/change-data/lab' },
  { label: 'Inbox', to: '/change-data/contact' },
  { label: 'Settings', to: '/change-data/settings' },
]

export default function AdminLayout() {
  const { logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/change-data/login', { replace: true })
  }

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div>
          <Link className="admin-wordmark" to="/change-data">
            SP<span>.</span>
          </Link>
          <p className="admin-sidebar-label">Change data</p>
        </div>

        <nav className="admin-nav" aria-label="Admin navigation">
          {adminNav.map((item) => (
            <NavLink
              key={item.to}
              className={({ isActive }) => `admin-nav-link${isActive ? ' is-active' : ''}`}
              end={item.end}
              to={item.to}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="admin-sidebar-foot">
          <Link className="admin-sidebar-link" to="/">
            View public site
          </Link>
          <button className="admin-sidebar-link" onClick={handleLogout} type="button">
            Sign out
          </button>
        </div>
      </aside>

      <div className="admin-main">
        <header className="admin-topbar">
          <div>
            <p className="admin-kicker">Portfolio control room</p>
            <p className="admin-topbar-title">Content that ships to the public site.</p>
          </div>
          <Link className="button button--small" to="/">
            View site
          </Link>
        </header>
        <main className="admin-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
