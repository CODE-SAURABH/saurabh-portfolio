export type ProjectCategory = 'ai' | 'vision' | 'tools' | 'product'

export type ProjectVisualVariant = 'rag' | 'vision' | 'nodes' | 'journal' | 'utility'

export interface Project {
  slug: string
  index: string
  title: string
  type: string
  category: ProjectCategory
  categoryLabel: string
  year: string
  description: string
  visual: ProjectVisualVariant
  technologies: string[]
  featured?: boolean
}

export type ProjectCardVariant = 'feature' | 'wide' | 'third'

export interface PublicProjectTechnology {
  name: string
}

export interface PublicProject {
  id: string
  title: string
  slug: string
  short_description: string | null
  category: ProjectCategory
  visual_type: ProjectVisualVariant | null
  is_featured: boolean
  display_order: number
  github_url: string | null
  live_url: string | null
  thumbnail_url: string | null
  technologies: PublicProjectTechnology[]
}

export interface PublicProjectCollection {
  data: PublicProject[]
  meta: {
    total: number
    offset: number
    limit: number
  }
}

export interface AdminProjectTechnology {
  id: string
  name: string
  display_order: number
}

export interface AdminProjectSection {
  id: string
  overline: string | null
  title: string
  body: string | null
  display_order: number
}

export interface AdminProjectListItem {
  id: string
  title: string
  slug: string
  short_description: string | null
  long_description: string | null
  status: string | null
  category: ProjectCategory
  visual_type: ProjectVisualVariant | null
  is_published: boolean
  is_featured: boolean
  display_order: number
  github_url: string | null
  live_url: string | null
  thumbnail_url: string | null
  created_at: string
  updated_at: string
  technologies: AdminProjectTechnology[]
}

export interface AdminProject extends AdminProjectListItem {
  sections: AdminProjectSection[]
}

export interface ProjectFormValues {
  title: string
  slug: string
  short_description: string
  long_description: string
  status: string
  category: ProjectCategory
  visual_type: ProjectVisualVariant | ''
  is_published: boolean
  is_featured: boolean
  display_order: number
  github_url: string
  live_url: string
  thumbnail_url: string
}

export interface ProjectSectionFormValues {
  overline: string
  title: string
  body: string
  display_order: number
}
