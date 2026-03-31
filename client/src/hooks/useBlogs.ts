import { useState } from 'react'
import type { Blog } from '../dtos/Blog'

const API_URL = import.meta.env.VITE_API_URL ?? ''

export function useBlogs() {
  const [blogs, setBlogs] = useState<Blog[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  async function fetchBlogs() {
    setLoading(true)
    setError(null)
    fetch(`${API_URL}/blogs`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server returned ${res.status}`)
        return res.json() as Promise<Blog[]>
      })
      .then((data) => {
        setBlogs(data)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }

  return { blogs, error, loading, fetchBlogs }
}
