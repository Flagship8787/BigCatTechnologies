import { useState } from 'react'
import type { BlogWithPosts } from '../dtos/Blog'

const API_URL = import.meta.env.VITE_API_URL ?? ''

export function useBlog() {
  const [blog, setBlog] = useState<BlogWithPosts | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  async function fetchBlog(blogId: string) {
    setLoading(true)
    setError(null)
    fetch(`${API_URL}/blogs/${blogId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server returned ${res.status}`)
        return res.json() as Promise<BlogWithPosts>
      })
      .then((data) => {
        setBlog(data)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }

  return { blog, error, loading, fetchBlog }
}
