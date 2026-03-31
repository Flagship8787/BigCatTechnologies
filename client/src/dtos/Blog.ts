import type { Post } from './Post'

export interface Blog {
  id: string
  name: string
  description: string
  created_at: string
  updated_at: string
}

export interface BlogWithPosts extends Blog {
  posts: Post[]
}
