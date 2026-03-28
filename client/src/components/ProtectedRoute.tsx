import { useAuth0 } from '@auth0/auth0-react'
import type { ReactNode } from 'react'

interface Props {
  children: ReactNode
}

export default function ProtectedRoute({ children }: Props) {
  const { isAuthenticated, isLoading, loginWithRedirect } = useAuth0()

  if (isLoading) {
    return <div className="auth-loading">Loading…</div>
  }

  if (!isAuthenticated) {
    loginWithRedirect({ appState: { returnTo: window.location.pathname } })
    return null
  }

  return <>{children}</>
}
