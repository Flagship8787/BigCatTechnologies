import { useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  IconButton,
  CircularProgress,
  Typography,
  Button,
  Chip,
  Tooltip,
  Box,
  Stack,
  Divider,
} from '@mui/material'
import { PageContainer } from '@toolpad/core/PageContainer'
import VisibilityIcon from '@mui/icons-material/Visibility'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import PublishIcon from '@mui/icons-material/Publish'
import UnpublishedIcon from '@mui/icons-material/Unpublished'
import XIcon from '@mui/icons-material/X'
import { useBlog } from '../../hooks/admin/useBlog'
import { usePost } from '../../hooks/admin/usePost'

export default function BlogDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { blog, error, loading, refreshData } = useBlog()
  const { publish, unpublish, tweet } = usePost()

  useEffect(() => {
    if (id) refreshData(id)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  const handlePublish = useCallback(async (postId: string) => {
    try {
      await publish(postId)
      if (id) refreshData(id)
    } catch (err) {
      console.error('Failed to publish post:', err)
    }
  }, [publish, refreshData, id])

  const handleUnpublish = useCallback(async (postId: string) => {
    try {
      await unpublish(postId)
      if (id) refreshData(id)
    } catch (err) {
      console.error('Failed to unpublish post:', err)
    }
  }, [unpublish, refreshData, id])

  const handleTweet = useCallback(async (postId: string) => {
    try {
      const result = await tweet(postId)
      window.open(result.url, '_blank')
    } catch (err) {
      console.error('Failed to tweet post:', err)
    }
  }, [tweet])

  return (
    <PageContainer title={blog?.name ?? 'Blog'}>
      {loading && <CircularProgress />}
      {error && <Typography color="error">{error}</Typography>}
      {!loading && !error && blog && (
        <>
          {/* Blog attributes */}
          <Stack spacing={1} sx={{ mb: 3 }}>
            {blog.description && (
              <Typography variant="body1" color="text.secondary">{blog.description}</Typography>
            )}
            <Stack direction="row" spacing={3}>
              <Typography variant="body2" color="text.secondary">
                Created: {new Date(blog.created_at).toLocaleDateString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Updated: {new Date(blog.updated_at).toLocaleDateString()}
              </Typography>
            </Stack>
          </Stack>

          <Divider sx={{ mb: 3 }} />

          {/* Posts section header */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h5">Posts</Typography>
            <Button variant="contained" onClick={() => navigate(`/admin/blogs/${id}/posts/new`)}>
              + Create New Post
            </Button>
          </Box>

          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Title</TableCell>
                <TableCell>State</TableCell>
                <TableCell>Created</TableCell>
                <TableCell>Updated</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {blog.posts.map((post) => (
                <TableRow key={post.id}>
                  <TableCell>{post.title}</TableCell>
                  <TableCell>
                    <Chip
                      label={post.state}
                      color={post.state === 'published' ? 'success' : post.state === 'drafted' ? 'default' : 'error'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{new Date(post.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>{new Date(post.updated_at).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <IconButton aria-label="view" onClick={() => navigate(`/admin/posts/${post.id}`)}>
                      <VisibilityIcon />
                    </IconButton>
                    <IconButton aria-label="edit" onClick={() => navigate(`/admin/posts/${post.id}/edit`)}>
                      <EditIcon />
                    </IconButton>
                    {post.state === 'drafted' && (
                      <IconButton aria-label="publish" onClick={() => handlePublish(post.id)}>
                        <PublishIcon />
                      </IconButton>
                    )}
                    {post.state === 'published' && (
                      <Tooltip title="Unpublish post">
                        <IconButton aria-label="unpublish" onClick={() => handleUnpublish(post.id)}>
                          <UnpublishedIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    {post.state === 'published' && (
                      <Tooltip title="Tweet this post">
                        <IconButton aria-label="tweet" onClick={() => handleTweet(post.id)}>
                          <XIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                    <IconButton aria-label="delete">
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </>
      )}
    </PageContainer>
  )
}
