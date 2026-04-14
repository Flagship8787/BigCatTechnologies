import { useEffect, useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'

function decodeJwtPayload(token: string): Record<string, unknown> {
  const payload = token.split('.')[1]
  return JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
}

export function usePermissions() {
  const { getAccessTokenSilently, isAuthenticated } = useAuth0()
  const [permissions, setPermissions] = useState<string[] | null>(null)

  useEffect(() => {
    if (!isAuthenticated) {
      setPermissions([])
      return
    }
    getAccessTokenSilently()
      .then((token) => {
        const payload = decodeJwtPayload(token)
        const perms = payload.permissions
        setPermissions(Array.isArray(perms) ? perms : [])
      })
      .catch(() => setPermissions([]))
  }, [isAuthenticated, getAccessTokenSilently])

  return { permissions, isLoading: permissions === null }
}
