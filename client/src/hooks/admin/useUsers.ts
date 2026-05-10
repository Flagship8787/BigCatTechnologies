import { useState } from "react"
import { useAuth0 } from "@auth0/auth0-react"
import type { User } from "../../dtos/User"

const API_URL = import.meta.env.VITE_API_URL ?? ""

export function useUsers() {
  const [users, setUsers] = useState<User[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const { getAccessTokenSilently } = useAuth0()

  async function fetchUsers() {
    setLoading(true)
    setError(null)
    getAccessTokenSilently()
      .then((token) =>
        fetch(`${API_URL}/admin/users`, {
          headers: { Authorization: `Bearer ${token}` },
        })
      )
      .then((res) => {
        if (!res.ok) throw new Error(`Server returned ${res.status}`)
        return res.json() as Promise<User[]>
      })
      .then((data) => {
        setUsers(data)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }

  return { users, error, loading, fetchUsers }
}
