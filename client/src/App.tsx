import './App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <span className="wordmark">BigCat Technologies</span>
        <nav className="nav">
          <a href="/mcp">MCP</a>
          <a href="/about">About</a>
          <a href="/contact">Contact</a>
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

export default App
