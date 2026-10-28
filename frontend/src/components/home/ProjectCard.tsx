import { Link } from 'react-router-dom'
import type { Project, ProjectCardVariant } from '../../types/project'
import { ProjectVisual } from './ProjectVisual'

interface ProjectCardProps {
  project: Project
  variant: ProjectCardVariant
}

export function ProjectCard({ project, variant }: ProjectCardProps) {
  const caseStudyPath = `/projects/${project.slug}`

  return (
    <article className={`project-card project-card--${variant}`} data-reveal>
      <ProjectVisual variant={project.visual} />

      <div className="project-copy">
        <div className="project-meta">
          <span className="project-type">{project.type}</span>
          <span>
            {project.index} — {project.categoryLabel}
          </span>
        </div>

        <div className="project-title-row">
          <h3 className="project-title">
            <Link to={caseStudyPath}>{project.title}</Link>
          </h3>
          <Link
            className="project-open"
            to={caseStudyPath}
            aria-label={`Open ${project.title} case study`}
          >
            ↗
          </Link>
        </div>

        <p className="project-desc">{project.description}</p>

        <div className="project-foot">
          <div className="tags">
            {project.technologies.slice(0, 3).map((technology) => (
              <span className="tag" key={technology}>
                {technology}
              </span>
            ))}
          </div>
          <Link className="text-link text-link--small" to={caseStudyPath}>
            Case study <span aria-hidden="true">→</span>
          </Link>
        </div>
      </div>
    </article>
  )
}
