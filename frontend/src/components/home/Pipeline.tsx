import { useState } from 'react'
import { pipelineStages } from '../../data/content'

type StageId = (typeof pipelineStages)[number]['id']

export function Pipeline() {
  const [activeId, setActiveId] = useState<StageId>(pipelineStages[0].id)
  const activeStage =
    pipelineStages.find((stage) => stage.id === activeId) ?? pipelineStages[0]

  return (
    <div className="pipeline" data-reveal style={{ animationDelay: '80ms' }}>
      <div className="pipeline-head">
        <span className="card-label">A small operating loop</span>
        <span className="pipeline-count">03 stages</span>
      </div>

      <div className="pipeline-stages">
        {pipelineStages.map((stage) => (
          <button
            key={stage.id}
            className="pipeline-stage"
            type="button"
            aria-pressed={activeId === stage.id}
            aria-controls="pipeline-detail"
            onClick={() => setActiveId(stage.id)}
          >
            <span className="stage-index">{stage.index}</span>
            <span className="stage-name">{stage.name}</span>
            <span className="stage-state">{activeId === stage.id ? stage.state : '—'}</span>
          </button>
        ))}
      </div>

      <div className="pipeline-detail" id="pipeline-detail" aria-live="polite">
        <span className="pipeline-detail-label">
          {activeStage.index} / {activeStage.name}
        </span>
        <p key={activeStage.id} className="pipeline-detail-copy">{activeStage.detail}</p>
      </div>
    </div>
  )
}
