export interface Profile {
  id: string
  full_name: string
  headline: string
  bio: string | null
  location: string | null
  email: string | null
  github_url: string | null
  linkedin_url: string | null
  website_url: string | null
  avatar_url: string | null
  availability_note: string | null
  updated_at: string
}

export interface ProfileFormValues {
  full_name: string
  headline: string
  bio: string
  location: string
  email: string
  github_url: string
  linkedin_url: string
  website_url: string
  avatar_url: string
  availability_note: string
}
