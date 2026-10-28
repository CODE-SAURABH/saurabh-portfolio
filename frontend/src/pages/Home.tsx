import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { HeroDiagram } from '../components/home/HeroDiagram'
import { Pipeline } from '../components/home/Pipeline'
import { ProjectCard } from '../components/home/ProjectCard'
import { Ticker } from '../components/home/Ticker'
import { ButtonLink } from '../components/ui/ButtonLink'
import { featuredProjects as fallbackProjects, principles } from '../data/content'
import { publicApi } from '../lib/publicApi'
import type { Profile } from '../types/profile'
import type {
  Project,
  ProjectCategory,
  PublicProject,
  PublicProjectCollection,
} from '../types/project'

const categoryMeta: Record<ProjectCategory, { label: string; type: string }> = {
  ai: { label: 'AI system', type: 'AI system / RAG' },
  vision: { label: 'Machine learning', type: 'Computer vision' },
  tools: { label: 'Developer tools', type: 'Developer tools' },
  product: { label: 'Product design', type: 'Product concept' },
}

function toProjectCard(project: PublicProject, index: number): Project {
  return {
    slug: project.slug,
    index: String(index + 1).padStart(2, '0'),
    title: project.title,
    type: categoryMeta[project.category].type,
    category: project.category,
    categoryLabel: categoryMeta[project.category].label,
    year: '',
    description: project.short_description ?? '',
    visual: project.visual_type ?? 'utility',
    technologies: project.technologies.map((technology) => technology.name),
    featured: project.is_featured,
  }
}

export default function Home() {
  const [projects, setProjects] = useState<Project[]>(fallbackProjects)
  const [profile, setProfile] = useState<Profile | null>(null)

  useEffect(() => {
    let active = true

    publicApi
      .get<PublicProjectCollection>('/projects', {
        params: { featured: true, limit: 3 },
      })
      .then((response) => {
        if (active && response.data.data.length > 0) {
          setProjects(response.data.data.map(toProjectCard))
        }
      })
      .catch(() => undefined)

    publicApi
      .get<{ data: Profile }>('/profile')
      .then((response) => {
        if (active) {
          setProfile(response.data.data)
        }
      })
      .catch(() => undefined)

    return () => {
      active = false
    }
  }, [])

  const firstName = profile?.full_name.trim().split(/\s+/)[0] || 'Saurabh'
  const location = profile?.location || 'Maharashtra, India'
  const availability = profile?.availability_note || 'Building in public'

  return (
    <>
      <section className="hero">
        <div className="container hero-grid">
          <div className="hero-copy">
            <p className="eyebrow" data-reveal>
              Computer science / AI engineering
            </p>

            <div className="hero-kickers" data-reveal style={{ animationDelay: '60ms' }}>
              <span className="kicker">01.5 years in tech</span>
              <span className="kicker">Builder mindset</span>
              <span className="kicker">India / IST</span>
            </div>

            <h1 className="hero-title" data-reveal style={{ animationDelay: '110ms' }}>
              <span className="hero-title-line">Intelligence</span>
              <span className="hero-title-line">should be</span>
              <span className="hero-title-line hero-title-accent">useful.</span>
            </h1>

            <p className="hero-lede" data-reveal style={{ animationDelay: '170ms' }}>
              I&apos;m {firstName}, a software engineer exploring AI-powered systems. I care about the
              whole loop: the data, the model, the interface, and whether the result earns a place
              in someone&apos;s day.
            </p>

            <div className="hero-actions" data-reveal style={{ animationDelay: '230ms' }}>
              <ButtonLink to="/contact" variant="primary">
                Let&apos;s talk <span className="arrow" aria-hidden="true">→</span>
              </ButtonLink>
              <ButtonLink to="/projects">
                See selected work <span className="arrow" aria-hidden="true">↗</span>
              </ButtonLink>
            </div>

            <dl className="hero-facts" data-reveal style={{ animationDelay: '290ms' }}>
              <div className="hero-fact">
                <dt>Based in</dt>
                <dd>{location}</dd>
              </div>
              <div className="hero-fact">
                <dt>Focus</dt>
                <dd>AI systems / backend</dd>
              </div>
              <div className="hero-fact">
                <dt>Currently</dt>
                <dd>{availability}</dd>
              </div>
            </dl>
          </div>

          <div className="hero-system-stack">
            <HeroDiagram />
            <aside className="hero-focus-card" data-reveal style={{ animationDelay: '240ms' }}>
              <div className="hero-focus-head">
                <span className="card-label">Operating focus</span>
                <span className="hero-focus-status"><i className="status-dot" /> Active</span>
              </div>
              <p>Turning AI capability into software people can actually use.</p>
              <div className="hero-focus-signals">
                <span><b>01</b> Context</span>
                <span><b>02</b> Interface</span>
                <span><b>03</b> Outcome</span>
              </div>
            </aside>
          </div>
        </div>
      </section>

      <Ticker />

      <section className="section" id="work">
        <div className="container">
          <div className="section-head" data-reveal>
            <div>
              <p className="section-index">01 / Selected work</p>
              <h2>
                Things I&apos;ve built
                <br />
                and learned from<span className="accent">.</span>
              </h2>
            </div>
            <p className="section-intro">
              A small set of projects across retrieval, computer vision, and developer tooling. The
              common thread is understanding the system end to end.
            </p>
          </div>

          <div className="project-grid">
            {projects.map((project, index) => (
              <ProjectCard
                key={project.slug}
                project={project}
                variant={index === 0 ? 'feature' : 'wide'}
              />
            ))}
          </div>

          <div className="section-foot">
            <Link className="text-link" to="/projects">
              All projects <span aria-hidden="true">→</span>
            </Link>
          </div>
        </div>
      </section>

      <section className="section section--tight">
        <div className="container">
          <div className="section-head" data-reveal>
            <div>
              <p className="section-index">02 / Engineering point of view</p>
              <h2>
                A model is one component<span className="accent">.</span>
              </h2>
            </div>
            <p className="section-intro">
              Useful AI comes from the system around the model: the context it receives, the tools
              it can use, and the interface that makes the result trustworthy.
            </p>
          </div>

          <div className="pov-grid">
            <div className="pov-copy" data-reveal>
              <span className="card-label">How I approach the work</span>
              <p className="pov-quote">
                &ldquo;Start with the problem. Keep the architecture legible. Make the result useful
                beyond the demo.&rdquo;
              </p>
              <p className="pov-note">
                <i className="status-dot" /> Clarity over cleverness / iteration over assumption
              </p>
            </div>
            <Pipeline />
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="about-grid">
            <article className="about-card about-card--primary" data-reveal>
              <span className="card-label">03 / About</span>
              <div className="about-year">
                2024<span>.</span>
                <small>B.Tech / Computer Science</small>
              </div>
              <h2>
                Curious about the <span className="accent">how.</span>
                <br />
                Intentional about the <span className="accent">why.</span>
              </h2>
              <p>
                I graduated in Computer Science and Engineering in 2024 and have been building my
                software foundation while exploring how AI can solve real problems. I&apos;m less
                interested in making every project look like a breakthrough, and more interested in
                explaining the problem honestly and improving the craft.
              </p>
              <Link className="text-link" to="/about">
                More about me <span aria-hidden="true">→</span>
              </Link>
            </article>

            <aside
              className="about-card about-card--secondary"
              data-reveal
              style={{ animationDelay: '80ms' }}
            >
              <span className="card-label">Currently curious about</span>
              <ul className="principles">
                {principles.map((principle) => (
                  <li className="principle" key={principle.index}>
                    <span className="principle-index">{principle.index}</span>
                    <div>
                      <h3>{principle.title}</h3>
                      <p>{principle.description}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </aside>
          </div>
        </div>
      </section>

      <section className="section section--tight">
        <div className="container">
          <div className="cta-band" data-reveal>
            <div className="cta-copy">
              <p className="section-index">04 / Next</p>
              <h2>
                Have a problem worth making <span className="accent">clearer?</span>
              </h2>
              <p>
                I&apos;m open to conversations about AI engineering, software roles, and projects
                where thoughtful systems matter.
              </p>
            </div>
            <ButtonLink to="/contact" variant="primary">
              Start a conversation <span className="arrow" aria-hidden="true">→</span>
            </ButtonLink>
          </div>
        </div>
      </section>
    </>
  )
}
