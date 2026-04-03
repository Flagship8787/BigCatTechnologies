import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  CircularProgress,
  Typography,
  Button,
  Box,
  Chip,
  Divider,
  Paper,
} from '@mui/material'
import { useAuth0 } from '@auth0/auth0-react'
import type { Post } from '../../dtos/Post'

const API_URL = import.meta.env.VITE_API_URL ?? ''

export default function PostDetails() {
  const { postId } = useParams<{ postId: string }>()
  const navigate = useNavigate()
  const { getAccessTokenSilently } = useAuth0()

  const [post, setPost] = useState<Post | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [publishing, setPublishing] = useState(false)
  const [publishError, setPublishError] = useState<string | null>(null)

  async function fetchPost() {
    setLoading(true)
    setError(null)
    try {
      const token = await getAccessTokenSilently()
      const res = await fetch(`${API_URL}/posts/${postId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error(`Server returned ${res.status}`)
      const data = await res.json() as Post
      setPost(data)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  async function handlePublish() {
    if (!post) return
    setPublishing(true)
    setPublishError(null)
    try {
      const token = await getAccessTokenSilently()
      const res = await fetch(`${API_URL}/admin/posts/${postId}/publish`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body.detail ?? `Server returned ${res.status}`)
      }
      const updated = await res.json() as Post
      setPost(updated)
    } catch (err) {
      setPublishError((err as Error).message)
    } finally {
      setPublishing(false)
    }
  }

  useEffect(() => {
    if (postId) fetchPost()
  }, [postId])

  return (
    <>
      <Button variant="text" onClick={() => navigate(-1)} sx={{ mb: 2 }}>
        ← Back
      </Button>

      {loading && <CircularProgress />}
      {error && <Typography color="error">{error}</Typography>}

      {!loading && !error && post && (
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Typography variant="h4">{post.title}</Typography>
            <Chip
              label={post.state}
              color={post.state === 'published' ? 'success' : post.state === 'drafted' ? 'default' : 'error'}
            />
          </Box>

          <Divider sx={{ mb: 2 }} />

          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Created: {new Date(post.created_at).toLocaleString()}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Last updated: {new Date(post.updated_at).toLocaleString()}
          </Typography>

          <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', mb: 3 }}>
            {post.body}
          </Typography>

          {publishError && (
            <Typography color="error" sx={{ mb: 2 }}>{publishError}</Typography>
          )}

          <Box sx={{ display: 'flex', gap: 2 }}>
            {post.state === 'drafted' && (
              <Button
                variant="contained"
                color="success"
                onClick={handlePublish}
                disabled={publishing}
              >
                {publishing ? 'Publishing…' : 'Publish'}
              </Button>
            )}
            <Button
              variant="outlined"
              onClick={() => navigate(`/admin/posts/${post.id}/edit`)}
            >
              Edit
            </Button>
          </Box>
        </Paper>
      )}
    </>
  )
}
