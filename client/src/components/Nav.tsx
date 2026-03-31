import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth0 } from '@auth0/auth0-react'
import './Nav.css'

interface NavProps {
  variant?: 'public' | 'dashboard'
}

export default function Nav({ variant = 'public' }: NavProps) {
  const { isAuthenticated, isLoading, loginWithRedirect, logout, user } = useAuth0()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

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

  const displayName = user?.name || user?.email

  return (
    <nav className="nav">
      <Link to="/mcp">MCP</Link>
      <Link to="/blog">Mox's Blog</Link>
      <Link to="/about">About</Link>
      <Link to="/contact">Contact</Link>
      {!isLoading && (
        isAuthenticated ? (
          <div className="nav-user-menu" ref={menuRef}>
            <button
              className="nav-user-menu__trigger"
              onClick={() => setDropdownOpen(prev => !prev)}
            >
              Hello {displayName}
            </button>
            {dropdownOpen && (
              <div className="nav-user-menu__dropdown">
                <button
                  className="nav-user-menu__item"
                  onClick={() => { setDropdownOpen(false); navigate('/dashboard') }}
                >
                  Admin
                </button>
                <button
                  className="nav-user-menu__item"
                  onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        ) : (
          <button className="nav-button" onClick={() => loginWithRedirect()}>
            Log in
          </button>
        )
      )}
    </nav>
  )
}
