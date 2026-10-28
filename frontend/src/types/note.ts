export interface Note {
  id: string
  title: string
  slug: string
  topic_label: string | null
  category: string | null
  body: string | null
  published_at: string | null
}

export interface AdminNote extends Note {
  is_published: boolean
  created_at: string
  updated_at: string
}

export interface NoteFormValues {
  title: string
  slug: string
  topic_label: string
  category: string
  body: string
  is_published: boolean
  published_at: string
}
