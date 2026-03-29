import { useEffect } from 'react'
import { Link, useParams } from 'react-router-dom'
import '../App.css'
import './PostDetail.css'
import Nav from '../components/Nav'
import { usePost } from '../hooks/usePost'
import { useFormatDate } from '../hooks/useFormatDate'

export default function PostDetail() {
  const { postId } = useParams<{ postId: string }>()
  const { post, error, loading, fetchPost } = usePost()
  const { formatDate } = useFormatDate()

  useEffect(() => {
    if (!postId) return
    fetchPost(postId)
  }, [postId])

  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="wordmark" style={{ textDecoration: 'none' }}>
          BigCat Technologies
        </Link>
        <Nav />
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
