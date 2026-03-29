import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import '../App.css'
import './PostDetail.css'

const API_URL = import.meta.env.VITE_API_URL ?? ''

interface Post {
  id: string
  blog_id: string
  title: string
  body: string
  created_at: string
  updated_at: string
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

export default function PostDetail() {
  const { postId } = useParams<{ postId: string }>()
  const [post, setPost] = useState<Post | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!postId) return
    fetch(`${API_URL}/posts/${postId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server returned ${res.status}`)
        return res.json() as Promise<Post>
      })
      .then((data) => {
        setPost(data)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }, [postId])

  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="wordmark" style={{ textDecoration: 'none' }}>
          BigCat Technologies
        </Link>
        <nav className="nav">
          <a href="/mcp">MCP</a>
          <Link to="/blog">Mox's Blog</Link>
          <a href="/about">About</a>
          <a href="/contact">Contact</a>
        </nav>
      </header>

      <main className="app-main post-detail-main">
        {loading && <p className="blog-status">Loading…</p>}

        {error && (
          <p className="blog-status blog-error">Could not load post: {error}</p>
        )}

        {post && !loading && (
          <article className="post-detail">
            <header className="post-detail-header">
              <h1 className="post-detail-title">{post.title}</h1>
              <time className="post-detail-date" dateTime={post.created_at}>
                {formatDate(post.created_at)}
              </time>
            </header>
            <div className="post-detail-body">
              {post.body.split('\n').map((paragraph, i) =>
                paragraph.trim() ? <p key={i}>{paragraph}</p> : null
              )}
            </div>
          </article>
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} BigCat Technologies</p>
      </footer>
    </div>
  )
}
