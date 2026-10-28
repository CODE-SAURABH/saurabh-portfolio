import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom'
import { PublicLayout } from './components/layout/PublicLayout'
import { AuthProvider } from './features/admin/AuthContext'
import { ProtectedRoute } from './features/admin/ProtectedRoute'
import Home from './pages/Home'
import { NotFoundPage, StubPage } from './pages/StubPage'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminExperience from './pages/admin/AdminExperience'
import AdminLayout from './pages/admin/AdminLayout'
import AdminLogin from './pages/admin/AdminLogin'
import AdminNotes from './pages/admin/AdminNotes'
import AdminPlaceholder from './pages/admin/AdminPlaceholder'
import AdminProfile from './pages/admin/AdminProfile'
import AdminProjects from './pages/admin/AdminProjects'

const router = createBrowserRouter([
  {
    path: '/change-data/login',
    element: <AdminLogin />,
  },
  {
    path: '/change-data',
    element: <ProtectedRoute />,
    children: [
      {
        element: <AdminLayout />,
        children: [
          { index: true, element: <AdminDashboard /> },
          { path: 'profile', element: <AdminProfile /> },
          { path: 'experience', element: <AdminExperience /> },
          { path: 'projects', element: <AdminProjects /> },
          { path: 'lab', element: <AdminNotes /> },
          {
            path: 'contact',
            element: (
              <AdminPlaceholder
                title="Contact inbox"
                description="Read submissions, mark them as read, and review notification status."
              />
            ),
          },
          {
            path: 'settings',
            element: (
              <AdminPlaceholder
                title="Site settings"
                description="Control the site title, tagline, social image, and resume download URL."
              />
            ),
          },
          { path: '*', element: <Navigate to="/change-data" replace /> },
        ],
      },
    ],
  },
  {
    path: '/',
    element: <PublicLayout />,
    children: [
      { index: true, element: <Home /> },
      {
        path: 'about',
        element: (
          <StubPage
            eyebrow="About / The human layer"
            title={
              <>
                Curious about the <span className="accent">how.</span>
              </>
            }
            lede="The longer story: education, the move into software, and the questions that keep pulling me toward AI."
          />
        ),
      },
      {
        path: 'experience',
        element: (
          <StubPage
            eyebrow="Experience / The path so far"
            title={
              <>
                Foundations, then <span className="accent">practice.</span>
              </>
            }
            lede="A clear timeline of the roles, responsibilities, and lessons that shaped how I work."
          />
        ),
      },
      {
        path: 'projects',
        element: (
          <StubPage
            eyebrow="Work / Selected projects"
            title={
              <>
                Built to be <span className="accent">understood.</span>
              </>
            }
            lede="Case studies across AI systems, computer vision, developer tooling, and product concepts."
          />
        ),
      },
      {
        path: 'projects/:slug',
        element: (
          <StubPage
            eyebrow="Work / Case study"
            title={
              <>
                The problem, approach, and <span className="accent">trade-offs.</span>
              </>
            }
            lede="A closer look at the decisions behind the project, what worked, and what comes next."
          />
        ),
      },
      {
        path: 'lab',
        element: (
          <StubPage
            eyebrow="Lab / Notes and experiments"
            title={
              <>
                Thinking out loud<span className="accent">.</span>
              </>
            }
            lede="Short engineering notes, experiments, and the questions currently on my desk."
          />
        ),
      },
      {
        path: 'resume',
        element: (
          <StubPage
            eyebrow="Resume / The short version"
            title={
              <>
                Experience, skills, and <span className="accent">signal.</span>
              </>
            }
            lede="A concise overview of my background, with a downloadable copy when the final content lands."
          />
        ),
      },
      {
        path: 'contact',
        element: (
          <StubPage
            eyebrow="Contact / Start a conversation"
            title={
              <>
                Good work starts with a <span className="accent">question.</span>
              </>
            }
            lede="The contact form, direct email, and response expectations will live here."
          />
        ),
      },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
])

export default function App() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  )
}
