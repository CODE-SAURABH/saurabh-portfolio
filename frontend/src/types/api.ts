export interface ApiData<T> {
  data: T
}

export interface ApiErrorBody {
  error?: {
    code?: string
    message?: string
    detail?: unknown
  }
}
