import { useState } from 'react'
import type { Post } from '../dtos/Post'

const API_URL = import.meta.env.VITE_API_URL ?? ''

export function usePost() {
  const [post, setPost] = useState<Post | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  async function fetchPost(postId: string) {
    setLoading(true)
    setError(null)
    fetch(`${API_URL}/posts/${postId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server returned ${res.status}`)
        return res.json() as Promise<Post>
      })
      .then((data) => {
        setPost(data)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }

  return { post, error, loading, fetchPost }
}
