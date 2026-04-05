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
} from '@mui/material'
import VisibilityIcon from '@mui/icons-material/Visibility'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import PublishIcon from '@mui/icons-material/Publish'
import { useBlog } from '../../hooks/admin/useBlog'
import { usePost } from '../../hooks/admin/usePost'

export default function BlogDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { blog, error, loading, refreshData } = useBlog()
  const { publish } = usePost()

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

  return (
    <>
      {loading && <CircularProgress />}
      {error && <Typography color="error">{error}</Typography>}
      {!loading && !error && blog && (
        <>
          <Typography variant="h4" gutterBottom>{blog.name}</Typography>
          <Typography variant="h5" gutterBottom sx={{ mt: 3 }}>Posts</Typography>
          <Button variant="contained" sx={{ mb: 2 }} onClick={() => navigate(`/admin/blogs/${id}/posts/new`)}>+ Create New Post</Button>
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
    </>
  )
}
