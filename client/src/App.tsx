import { Routes, Route } from 'react-router-dom'
import { useAuth0 } from '@auth0/auth0-react'
import ProtectedRoute from './components/ProtectedRoute'
import Dashboard from './pages/Dashboard'
import './App.css'

function Home() {
  const { isAuthenticated, isLoading, loginWithRedirect, logout, user } = useAuth0()

  return (
    <div className="app">
      <header className="app-header">
        <span className="wordmark">BigCat Technologies</span>
        <nav className="nav">
          <a href="/mcp">MCP</a>
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
      </header>

      <main className="app-main">
        <section className="hero">
          <h1>BigCat Technologies</h1>
          <p className="tagline">The online laboratory of Sam Shapiro</p>
        </section>

        <section className="bio">
          <p>
            Full-stack engineer with nearly 20 years of professional experience building and
            scaling large-scale enterprise applications. Currently focused on pushing the limits
            of agentic development and the growing agentic ecosystem.
          </p>
          <p>
            Background spans engineering leadership at Bowery Valuation, 3D capture at Durst
            Imaging, and most recently Senior Full Stack Engineer at Peloton — where he built
            MCP interfaces for LLM integrations and designed core services for a logistics
            platform serving 25K+ weekly orders.
          </p>
          <p>
            Passionate about AI tooling, agentic workflows, and Jazz.
          </p>
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} BigCat Technologies</p>
      </footer>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}
