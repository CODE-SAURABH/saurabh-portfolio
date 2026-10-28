export interface Experience {
  id: string
  company: string
  role_title: string
  employment_type: string | null
  start_date: string
  end_date: string | null
  is_current: boolean
  description: string | null
  display_order: number
  created_at: string
  updated_at: string
}

export interface ExperienceFormValues {
  company: string
  role_title: string
  employment_type: string
  start_date: string
  end_date: string
  is_current: boolean
  description: string
  display_order: number
}
