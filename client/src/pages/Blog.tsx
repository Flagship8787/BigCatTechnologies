import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import '../App.css'
import './Blog.css'
import Nav from '../components/Nav'
import type { Post } from '../dtos/Post'
import { useFormatDate } from '../hooks/useFormatDate'

const BLOG_ID = 'd269d2a7-eecd-4cbf-b6e5-a48025933c7f'
const API_URL = import.meta.env.VITE_API_URL ?? ''

interface BlogData {
  id: string
  name: string
  description: string
  created_at: string
  updated_at: string
  posts: Post[]
}

function PostPreview({ post }: { post: Post }) {
  const { formatDate } = useFormatDate()
  const preview = post.body.length > 280 ? post.body.slice(0, 280).trimEnd() + '…' : post.body

  return (
    <article className="blog-post-preview">
      <Link to={`/blog/posts/${post.id}`} className="blog-post-title-link">
        <h2 className="blog-post-title">{post.title}</h2>
      </Link>
      <time className="blog-post-date" dateTime={post.created_at}>
        {formatDate(post.created_at)}
      </time>
      <p className="blog-post-body">{preview}</p>
    </article>
  )
}

export default function Blog() {
  const [blog, setBlog] = useState<BlogData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_URL}/blogs/${BLOG_ID}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Server returned ${res.status}`)
        return res.json() as Promise<BlogData>
      })
      .then((data) => {
        setBlog(data)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  const recentPosts = blog
    ? [...blog.posts]
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .slice(0, 5)
    : []

  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="wordmark" style={{ textDecoration: 'none' }}>
          BigCat Technologies
        </Link>
        <Nav />
      </header>

      <main className="app-main blog-main">
        {loading && <p className="blog-status">Loading…</p>}

        {error && (
          <p className="blog-status blog-error">Could not load blog: {error}</p>
        )}

        {blog && !loading && (
          <>
            <section className="hero">
              <h1>{blog.name}</h1>
              {blog.description && <p className="tagline">{blog.description}</p>}
            </section>

            <section className="blog-posts">
              {recentPosts.length === 0 ? (
                <p className="blog-status">No posts yet.</p>
              ) : (
                recentPosts.map((post) => <PostPreview key={post.id} post={post} />)
              )}
            </section>
          </>
        )}
      </main>

      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} BigCat Technologies</p>
      </footer>
    </div>
  )
}
