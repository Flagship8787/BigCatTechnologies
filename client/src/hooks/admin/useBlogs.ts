import { useState } from "react"
import { useAuth0 } from "@auth0/auth0-react"
import type { Blog } from "../../dtos/Blog"

const API_URL = import.meta.env.VITE_API_URL ?? ""

export function useBlogs() {
  const [blogs, setBlogs] = useState<Blog[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const { getAccessTokenSilently } = useAuth0()

  async function fetchBlogs() {
    setLoading(true)
    setError(null)
    getAccessTokenSilently()
      .then((token) =>
        fetch(`${API_URL}/admin/blogs`, {
          headers: { Authorization: `Bearer ${token}` },
        })
      )
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
