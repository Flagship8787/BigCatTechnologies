import { useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import type { Post } from '../../dtos/Post'

const API_URL = import.meta.env.VITE_API_URL ?? ''

export function usePost() {
  const [post, setPost] = useState<Post | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const { getAccessTokenSilently } = useAuth0()

  async function fetchData(postId: string) {
    setLoading(true)
    setError(null)
    try {
      const token = await getAccessTokenSilently()
      const res = await fetch(`${API_URL}/admin/posts/${postId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error(`Server returned ${res.status}`)
      const data = await res.json() as Post
      setPost(data)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  async function publish(postId: string): Promise<Post> {
    const token = await getAccessTokenSilently()
    const res = await fetch(`${API_URL}/admin/posts/${postId}/publish`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error((body as { detail?: string }).detail ?? `Server returned ${res.status}`)
    }
    const updated = await res.json() as Post
    setPost(updated)
    return updated
  }

  async function update(postId: string, values: { title: string; body: string; state: string }): Promise<Post> {
    const token = await getAccessTokenSilently()
    const res = await fetch(`${API_URL}/admin/posts/${postId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(values),
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error((body as { detail?: string }).detail ?? `Server returned ${res.status}`)
    }
    const updated = await res.json() as Post
    setPost(updated)
    return updated
  }

  async function tweet(postId: string): Promise<{ id: string; tweet_id: string; url: string }> {
    const token = await getAccessTokenSilently()
    const res = await fetch(`${API_URL}/admin/posts/${postId}/tweet`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error((body as { detail?: string }).detail ?? `Server returned ${res.status}`)
    }
    return res.json() as Promise<{ id: string; tweet_id: string; url: string }>
  }

  return { post, error, loading, fetchData, publish, update, tweet }
}
