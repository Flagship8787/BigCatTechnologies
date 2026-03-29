import { Link } from 'react-router-dom'
import { useAuth0 } from '@auth0/auth0-react'

interface NavProps {
  variant?: 'public' | 'dashboard'
}

export default function Nav({ variant = 'public' }: NavProps) {
  const { isAuthenticated, isLoading, loginWithRedirect, logout, user } = useAuth0()

  if (variant === 'dashboard') {
    return (
      <nav className="nav">
        <Link to="/">Home</Link>
        <button
          className="nav-button"
          onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
        >
          Log out
        </button>
      </nav>
    )
  }

  return (
    <nav className="nav">
      <a href="/mcp">MCP</a>
      <Link to="/blog">Mox's Blog</Link>
      <a href="/about">About</a>
      <a href="/contact">Contact</a>
      {!isLoading && (
        isAuthenticated ? (
          <>
            <a href="/dashboard">{user?.email}</a>
            <button
              className="nav-button"
              onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
            >
              Log out
            </button>
          </>
        ) : (
          <button className="nav-button" onClick={() => loginWithRedirect()}>
            Log in
          </button>
        )
      )}
    </nav>
  )
}
