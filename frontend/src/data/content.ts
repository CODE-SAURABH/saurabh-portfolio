import type { Project } from '../types/project'

export const site = {
  name: 'Saurabh Patil',
  role: 'AI / Software Engineer',
  location: 'Maharashtra, India',
  email: 'hello@example.com',
}

export const navItems = [
  { label: 'Home', to: '/' },
  { label: 'About', to: '/about' },
  { label: 'Experience', to: '/experience' },
  { label: 'Work', to: '/projects' },
  { label: 'Lab', to: '/lab' },
  { label: 'Contact', to: '/contact' },
]

export const heroNodes = [
  {
    id: 'context',
    label: 'CONTEXT',
    x: 16,
    y: 21,
    detail:
      'Retrieval, documents, user intent, and constraints. Start with the situation the system has to understand.',
  },
  {
    id: 'model',
    label: 'MODEL',
    x: 84,
    y: 21,
    detail:
      'The model is one component, not the whole system. Capability matters only when the surrounding product is useful.',
  },
  {
    id: 'data',
    label: 'DATA',
    x: 16,
    y: 79,
    detail:
      'Memory and state shape what the system can do. Clean inputs and honest retrieval are part of the product.',
  },
  {
    id: 'tools',
    label: 'TOOLS',
    x: 84,
    y: 79,
    detail:
      'APIs and tools turn reasoning into action. Clear boundaries make an agent easier to inspect and trust.',
  },
  {
    id: 'core',
    label: 'INTELLIGENCE',
    x: 50,
    y: 50,
    detail:
      'Correctness, latency, and trust are design decisions. The goal is a system that is useful beyond the demo.',
  },
] as const

export const pipelineStages = [
  {
    id: 'observe',
    index: '01',
    name: 'Observe',
    state: 'FRAME',
    detail:
      'Start with the actual constraint: what the user needs, what the data supports, and where the system can fail.',
  },
  {
    id: 'reason',
    index: '02',
    name: 'Reason',
    state: 'DESIGN',
    detail:
      'Choose the simplest architecture that earns its complexity. A model is one component, not the whole system.',
  },
  {
    id: 'act',
    index: '03',
    name: 'Act',
    state: 'SHIP',
    detail:
      'Ship the interface, evaluate the outcome, and keep the loop inspectable enough to improve in the next iteration.',
  },
] as const

export const projects: Project[] = [
  {
    slug: 'vidnyan-bot',
    index: '01',
    title: 'Vidnyan-Bot',
    type: 'AI system / RAG',
    category: 'ai',
    categoryLabel: 'AI system',
    year: '2025',
    description:
      'An educational science question-answering assistant built around retrieval-augmented generation and NCERT learning material.',
    visual: 'rag',
    technologies: ['LangChain', 'Embeddings', 'Vector search'],
    featured: true,
  },
  {
    slug: 'sugarcane-leaf-detection',
    index: '02',
    title: 'Sugarcane Leaf Disease Detection',
    type: 'Computer vision',
    category: 'vision',
    categoryLabel: 'Machine learning',
    year: '2024',
    description:
      'A machine-learning project exploring crop-leaf imagery and disease classification for an agriculture use case.',
    visual: 'vision',
    technologies: ['Python', 'Image processing', 'ML'],
    featured: true,
  },
  {
    slug: 'openskills',
    index: '03',
    title: 'OpenSkills',
    type: 'Developer tools',
    category: 'tools',
    categoryLabel: 'AI agents',
    year: '2025',
    description:
      'A developer-focused repository exploring reusable AI agent skills and tooling resources.',
    visual: 'nodes',
    technologies: ['AI agents', 'MCP', 'Documentation'],
    featured: true,
  },
  {
    slug: 'dayend-journal',
    index: '04',
    title: 'DayEnd Journal',
    type: 'Product concept',
    category: 'product',
    categoryLabel: 'Product design',
    year: '2025',
    description:
      'A personal productivity concept combining guided reflection, habit tracking, and weekly insights.',
    visual: 'journal',
    technologies: ['React', 'FastAPI', 'PWA concept'],
  },
  {
    slug: 'image-to-pdf',
    index: '05',
    title: 'Image to PDF Converter',
    type: 'Utility / product',
    category: 'tools',
    categoryLabel: 'Utility app',
    year: '2024',
    description:
      'A utility project focused on a simple workflow for combining images into a shareable document.',
    visual: 'utility',
    technologies: ['File handling', 'Utility app'],
  },
]

export const featuredProjects = projects.filter((project) => project.featured).slice(0, 3)

export const tickerItems = [
  'Retrieval',
  'Evaluation',
  'Backend',
  'Computer vision',
  'Developer tools',
  'Systems thinking',
  'AI engineering',
  'Product craft',
]

export const principles = [
  {
    index: 'A',
    title: 'Clarity',
    description: 'Make the problem legible before adding complexity.',
  },
  {
    index: 'B',
    title: 'Curiosity',
    description: 'Understand the whole loop, including the failure paths.',
  },
  {
    index: 'C',
    title: 'Craft',
    description: 'Ship accessible interfaces, maintainable code, and honest outcomes.',
  },
]
