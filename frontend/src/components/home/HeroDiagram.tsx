import { useState } from 'react'
import { heroNodes } from '../../data/content'

type NodeId = (typeof heroNodes)[number]['id']

const inputNodes = heroNodes.filter((node) => node.id === 'context' || node.id === 'data')
const orchestrationNodes = heroNodes.filter((node) => node.id === 'model' || node.id === 'tools')
const coreNode = heroNodes.find((node) => node.id === 'core') ?? heroNodes[0]

interface ModuleButtonProps {
  node: (typeof heroNodes)[number]
  activeId: NodeId
  onSelect: (id: NodeId) => void
}

function ModuleButton({ node, activeId, onSelect }: ModuleButtonProps) {
  const isActive = activeId === node.id

  return (
    <button
      className="system-module"
      type="button"
      aria-pressed={isActive}
      onClick={() => onSelect(node.id)}
    >
      <span className="system-module-index">0{heroNodes.indexOf(node) + 1}</span>
      <span>{node.label}</span>
      <i aria-hidden="true" />
    </button>
  )
}

export function HeroDiagram() {
  const [activeId, setActiveId] = useState<NodeId>('core')
  const activeNode = heroNodes.find((node) => node.id === activeId) ?? coreNode

  return (
    <div className="diagram" data-reveal style={{ animationDelay: '160ms' }}>
      <div className="diagram-head">
        <span>System / Intelligence</span>
        <span className="diagram-status">
          <i className="status-dot" /> Online
        </span>
      </div>

      <div className="system-map">
        <div className="system-lane">
          <span className="system-lane-label">Input</span>
          {inputNodes.map((node) => (
            <ModuleButton key={node.id} node={node} activeId={activeId} onSelect={setActiveId} />
          ))}
        </div>

        <div className="system-connector system-connector--left" aria-hidden="true" />

        <button
          className="system-core"
          type="button"
          aria-pressed={activeId === coreNode.id}
          onClick={() => setActiveId(coreNode.id)}
        >
          <span className="system-core-kicker">Processing layer</span>
          <strong>INTELLIGENCE</strong>
          <span className="system-core-state"><i /> Ready to reason</span>
        </button>

        <div className="system-connector system-connector--right" aria-hidden="true" />

        <div className="system-lane">
          <span className="system-lane-label">Orchestration</span>
          {orchestrationNodes.map((node) => (
            <ModuleButton key={node.id} node={node} activeId={activeId} onSelect={setActiveId} />
          ))}
        </div>
      </div>

      <div className="diagram-readout" aria-live="polite">
        <span className="diagram-readout-label">{activeNode.label} /</span>
        <p>{activeNode.detail}</p>
      </div>

      <div className="diagram-foot">
        <span>Architecture view</span>
        <span>Input → Reason → Action</span>
      </div>
    </div>
  )
}
