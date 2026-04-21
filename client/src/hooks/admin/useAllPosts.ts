import { useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import type { Blog } from '../../dtos/Blog'
import type { Post } from '../../dtos/Post'
import type { BlogWithPosts } from '../../dtos/Blog'

const API_URL = import.meta.env.VITE_API_URL ?? ''

export interface AllPostsResult {
  posts: Post[]
  blogMap: Record<string, string>
}

export function useAllPosts() {
  const [result, setResult] = useState<AllPostsResult>({ posts: [], blogMap: {} })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const { getAccessTokenSilently } = useAuth0()

  async function fetchAllPosts(blogs: Blog[]) {
    if (blogs.length === 0) {
      setResult({ posts: [], blogMap: {} })
      return
    }
    setLoading(true)
    setError(null)
    try {
      const token = await getAccessTokenSilently()
      const blogWithPostsResults = await Promise.all(
        blogs.map((blog) =>
          fetch(`${API_URL}/admin/blogs/${blog.id}`, {
            headers: { Authorization: `Bearer ${token}` },
          })
            .then((r) => (r.ok ? (r.json() as Promise<BlogWithPosts>) : null))
            .catch(() => null)
        )
      )
      const newBlogMap: Record<string, string> = {}
      const allPosts: Post[] = []
      for (const blogWithPosts of blogWithPostsResults) {
        if (blogWithPosts) {
          newBlogMap[blogWithPosts.id] = blogWithPosts.name
          allPosts.push(...blogWithPosts.posts)
        }
      }
      setResult({ posts: allPosts, blogMap: newBlogMap })
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return { ...result, loading, error, fetchAllPosts }
}
