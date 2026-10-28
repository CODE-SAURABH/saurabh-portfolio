import type { ProjectVisualVariant } from '../../types/project'

const sourceRows = [
  { type: 'PDF', name: 'class_09_science' },
  { type: 'PDF', name: 'class_10_science' },
  { type: 'TXT', name: 'chapter_notes' },
  { type: 'DB', name: 'embedded_chunks' },
]

const vectorBars = [30, 65, 42, 87, 55, 73, 32, 94, 45, 66, 85, 39, 62]

const nodeLabels = ['AGENT', 'MCP', 'TOOLS', 'SKILLS', 'LLM', 'FLOW', 'REPO', 'DOCS', 'DEVX']

export function ProjectVisual({ variant }: { variant: ProjectVisualVariant }) {
  if (variant === 'rag') {
    return (
      <div className="project-visual project-visual--rag" aria-hidden="true">
        <div className="visual-window">
          <div className="window-top">
            <i />
            <i />
            <i />
            <span>VIDNYAN / KNOWLEDGE FLOW</span>
          </div>
          <div className="rag-layout">
            <div className="rag-panel">
              <small>01 / Source material</small>
              {sourceRows.map((row) => (
                <div className="doc-row" key={row.name}>
                  <b className="doc-type">{row.type}</b>
                  {row.name}
                </div>
              ))}
            </div>
            <div className="rag-panel">
              <small>02 / Retrieval + response</small>
              <div className="vector-bars">
                {vectorBars.map((height, index) => (
                  <i key={index} style={{ height: `${height}%` }} />
                ))}
              </div>
              <div className="rag-chip">3 relevant passages retrieved</div>
              <div className="doc-row">
                <b className="doc-type">OUT</b>
                Grounded answer
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (variant === 'vision') {
    return (
      <div className="project-visual project-visual--vision" aria-hidden="true">
        <div className="leaf-visual">
          <span className="leaf-label">Vision model / conceptual scan</span>
          <svg viewBox="0 0 300 260" fill="none">
            <path
              d="M45 219C51 140 104 46 254 22C259 104 210 204 108 226C78 232 57 227 45 219Z"
              fill="var(--accent-subtle)"
              stroke="var(--accent)"
              strokeWidth="2"
            />
            <path d="M48 221C117 167 183 90 251 25" stroke="var(--accent)" strokeWidth="3" />
            <path
              d="M97 183L86 133M129 155L125 103M159 126L158 76M186 95L194 50M124 157L171 174M159 126L203 145M186 96L226 104"
              stroke="var(--accent)"
              strokeWidth="2"
              opacity="0.55"
            />
            <circle
              cx="144"
              cy="139"
              r="27"
              stroke="var(--accent)"
              strokeDasharray="4 6"
            />
            <path d="M144 111V83H199" stroke="var(--accent)" />
            <rect
              x="198"
              y="72"
              width="70"
              height="22"
              rx="4"
              fill="var(--bg-elevated)"
              stroke="var(--line-strong)"
            />
            <text
              x="206"
              y="86"
              fill="var(--accent)"
              fontSize="9"
              style={{ fontFamily: 'var(--font-mono)' }}
            >
              REGION / 01
            </text>
          </svg>
          <span className="leaf-coord">IMG // Classification</span>
        </div>
      </div>
    )
  }

  if (variant === 'nodes') {
    return (
      <div className="project-visual project-visual--nodes" aria-hidden="true">
        <div className="node-map">
          {nodeLabels.map((label) => (
            <span key={label}>{label}</span>
          ))}
        </div>
      </div>
    )
  }

  if (variant === 'journal') {
    return (
      <div className="project-visual project-visual--journal" aria-hidden="true">
        <div className="journal-card">
          <div className="journal-brand">
            dayend<span>.</span>
          </div>
          <div className="journal-kicker">Nightly check-in / 09:42 PM</div>
          <h4>
            Close the day
            <br />
            with intention.
          </h4>
          <div className="journal-line" />
          <div className="journal-line" />
          <div className="journal-line" />
          <div className="journal-bars">
            {[35, 77, 45, 92, 60, 80, 42].map((height, index) => (
              <i key={index} style={{ height: `${height}%` }} />
            ))}
          </div>
          <div className="journal-kicker">Reflection / consistency</div>
        </div>
      </div>
    )
  }

  return (
    <div className="project-visual project-visual--utility" aria-hidden="true">
      <div className="utility-window">
        <div className="window-top">
          <i />
          <i />
          <i />
          <span>IMAGE_TO_PDF</span>
        </div>
        <div className="utility-body">
          <div className="utility-file">IMG</div>
          <div className="utility-caption">
            + 4 images
            <br />
            →
            <br />
            <b>PDF ready</b>
          </div>
          <div className="utility-file utility-file--accent">PDF</div>
        </div>
      </div>
    </div>
  )
}
