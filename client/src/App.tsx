import { Routes, Route } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'
import Nav from './components/Nav'
import Dashboard from './admin/pages/Dashboard'
import Blog from './pages/Blog'
import PostDetail from './pages/PostDetail'
import AllBlogs from './admin/pages/AllBlogs'
import BlogDetail from './admin/pages/BlogDetail'
import CreateBlog from './admin/pages/CreateBlog'
import Mcp from './pages/Mcp'
import About from './pages/About'
import Contact from './pages/Contact'
import bigcatLogo from './assets/bigcat_logo.png'
import './App.css'

function Home() {
  return (
    <div className="app">
      <header className="app-header">
        <div className="wordmark-group">
          <img src={bigcatLogo} alt="BigCat Technologies logo" className="wordmark-logo" />
          <span className="wordmark">BigCat Technologies</span>
        </div>
        <Nav />
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
      <Route path="/mcp" element={<Mcp />} />
      <Route path="/about" element={<About />} />
      <Route path="/contact" element={<Contact />} />
      <Route path="/blog" element={<Blog />} />
      <Route path="/blog/posts/:postId" element={<PostDetail />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/blogs"
        element={
          <ProtectedRoute>
            <AllBlogs />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/blogs/:id"
        element={
          <ProtectedRoute>
            <BlogDetail />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/blogs/new"
        element={
          <ProtectedRoute>
            <CreateBlog />
          </ProtectedRoute>
        }
      />
    </Routes>
  )
}
