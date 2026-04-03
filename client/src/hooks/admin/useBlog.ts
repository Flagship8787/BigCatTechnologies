import { useState } from "react"
import { useAuth0 } from "@auth0/auth0-react"
import type { BlogWithPosts } from "../../dtos/Blog"

const API_URL = import.meta.env.VITE_API_URL ?? ""

export function useBlog() {
  const [blog, setBlog] = useState<BlogWithPosts | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const { getAccessTokenSilently } = useAuth0()

  async function refreshData(blogId: string) {
    setLoading(true)
    setError(null)
    getAccessTokenSilently()
      .then((token) =>
        fetch(`${API_URL}/admin/blogs/${blogId}`, {
          headers: { Authorization: `Bearer ${token}` },
        })
      )
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

  async function publish(postId: string): Promise<void> {
    const token = await getAccessTokenSilently()
    const res = await fetch(`${API_URL}/admin/posts/${postId}/publish`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) throw new Error(`Server returned ${res.status}`)
  }

  return { blog, error, loading, refreshData, publish }
}
