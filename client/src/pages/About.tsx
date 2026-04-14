import Nav from '../components/Nav'
import bigcatLogo from '../assets/bigcat_logo.png'
import '../App.css'
import './About.css'

export default function About() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="wordmark-group">
          <img src={bigcatLogo} alt="BigCat Technologies logo" className="wordmark-logo" />
          <span className="wordmark">BigCat Technologies</span>
        </div>
        <Nav />
      </header>

      <main className="app-main about-main">
        <section className="hero">
          <h1>About</h1>
          <p className="tagline">
            A one-person lab at the edge of what's possible with software and AI.
          </p>
        </section>

        <section className="about-body">
          <div className="about-block">
            <h2>What Is BigCat Technologies?</h2>
            <p>
              BigCat Technologies is the personal engineering laboratory of{' '}
              <strong>Sam Shapiro</strong> — a place where ideas get shipped, experiments run
              wild, and the agentic future gets built one commit at a time.
            </p>
            <p>
              It's not a startup. It's not a consultancy. It's a workshop — raw, iterative,
              and unapologetically ambitious. The kind of place where a new tool lands on
              Monday and it's in production by Thursday.
            </p>
          </div>

          <div className="about-block">
            <h2>The Work</h2>
            <p>
              Sam brings nearly two decades of engineering to the table — from scrappy
              startups to large-scale enterprise platforms. The résumé includes:
            </p>
            <ul className="about-list">
              <li>
                <strong>Peloton</strong> — Senior Full Stack Engineer building MCP interfaces
                for LLM integrations and core logistics services handling 25K+ weekly orders
              </li>
              <li>
                <strong>Bowery Valuation</strong> — Engineering leadership on valuation
                software used by commercial real estate firms across the US
              </li>
              <li>
                <strong>Durst Imaging</strong> — 3D capture systems and visual data pipelines
                for one of NYC's largest real estate portfolios
              </li>
              <li>
                <strong>10 years freelance</strong> — Across fintech, media, e-commerce, and
                every other vertical that needed something built fast and built right
              </li>
            </ul>
          </div>

          <div className="about-block">
            <h2>The Obsessions</h2>
            <p>
              Right now, the energy is concentrated at the intersection of <strong>AI
              tooling</strong>, <strong>agentic workflows</strong>, and{' '}
              <strong>Model Context Protocol</strong>. The goal: build systems that let AI
              agents do real work — not party tricks.
            </p>
            <p>
              When not shipping code, you'll find Sam on a mountain — rock or ice, it doesn't
              matter. An avid climber for years, he's happiest when the route goes up.
            </p>
          </div>

          <div className="about-block about-cta">
            <h2>Get In Touch</h2>
            <p>
              Curious about the work? Want to collaborate? Have a problem that needs
              an engineer who actually gives a damn?
            </p>
            <a href="/contact" className="about-link">Say hello →</a>
          </div>
        </section>
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} BigCat Technologies</p>
      </footer>
    </div>
  )
}
