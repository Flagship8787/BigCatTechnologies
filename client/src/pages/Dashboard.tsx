import { useAuth0 } from '@auth0/auth0-react'
import '../App.css'
import './Dashboard.css'

export default function Dashboard() {
  const { user, logout } = useAuth0()

  return (
    <div className="app">
      <header className="app-header">
        <span className="wordmark">BigCat Technologies</span>
        <nav className="nav">
          <a href="/">Home</a>
          <button
            className="nav-button"
            onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
          >
            Log out
          </button>
        </nav>
      </header>

      <main className="app-main">
        <section className="hero">
          <h1>Dashboard</h1>
          <p className="tagline">Welcome back, {user?.email}</p>
        </section>

        <section className="bio">
          <p>You are authenticated. This is a protected area of the site.</p>
          {user?.picture && (
            <img
              src={user.picture}
              alt={user.name ?? 'Profile'}
              className="dashboard-avatar"
            />
          )}
          <p><strong style={{ color: '#fff' }}>Name:</strong> {user?.name}</p>
          <p><strong style={{ color: '#fff' }}>Email:</strong> {user?.email}</p>
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} BigCat Technologies</p>
      </footer>
    </div>
  )
}
