export interface Education {
  id: string
  institution: string
  degree: string
  field: string | null
  start_date: string
  end_date: string | null
  description: string | null
  display_order: number
}

export interface SkillItem {
  id: string
  name: string
  is_featured: boolean
  display_order: number
}

export interface SkillGroup {
  id: string
  name: string
  display_order: number
  skills: SkillItem[]
}

export interface ContactForm {
  name: string
  email: string
  subject: string
  message: string
}

export interface SiteSettings {
  site_title: string
  tagline: string | null
  og_image_url: string | null
  resume_download_url: string | null
}

export interface PublicProject {
  id: string
  title: string
  slug: string
  short_description: string | null
  category: string
  visual_type: string | null
  is_featured: boolean
  display_order: number
  github_url: string | null
  live_url: string | null
  thumbnail_url: string | null
  technologies: { name: string }[]
}

export interface PublicProjectDetail extends PublicProject {
  long_description: string | null
  status: string | null
  sections: {
    id: string
    overline: string | null
    title: string
    body: string | null
    display_order: number
  }[]
}

export interface Note {
  id: string
  title: string
  slug: string
  topic_label: string | null
  category: string | null
  body: string | null
  published_at: string | null
  status: string | null
}

export interface ApiCollection<T> {
  data: T[]
  meta: { total: number; offset: number; limit: number }
}
