import { useEffect, useState, useCallback } from 'react'
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
import ArrowBackIcon from '@mui/icons-material/ArrowBack'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { usePost } from '../../hooks/admin/usePost'

export default function PostDetails() {
  const { postId } = useParams<{ postId: string }>()
  const navigate = useNavigate()
  const { post, loading, error, fetchData, publish } = usePost()

  const [publishing, setPublishing] = useState(false)
  const [publishError, setPublishError] = useState<string | null>(null)

  useEffect(() => {
    if (postId) fetchData(postId)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [postId])

  const handlePublish = useCallback(async () => {
    if (!postId) return
    setPublishing(true)
    setPublishError(null)
    try {
      await publish(postId)
    } catch (err) {
      setPublishError((err as Error).message)
    } finally {
      setPublishing(false)
    }
  }, [postId, publish])

  return (
    <>
      <Button variant="text" onClick={() => navigate(-1)} sx={{ mb: 2 }} startIcon={<ArrowBackIcon />}>
        Back
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

          <Box sx={{ mb: 3 }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {post.body}
            </ReactMarkdown>
          </Box>

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
