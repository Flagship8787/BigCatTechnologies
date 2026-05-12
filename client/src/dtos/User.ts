export interface User {
  id: string
  auth0_id: string
  email: string | null
  email_verified: boolean | null
  name: string | null
  picture: string | null
  created_at: string
  updated_at: string
}
