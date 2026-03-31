import { useEffect } from 'react'
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
} from '@mui/material'
import VisibilityIcon from '@mui/icons-material/Visibility'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import AdminLayout from '../layouts/AdminLayout'
import { useBlog } from '../../hooks/useBlog'

export default function BlogDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { blog, error, loading, fetchBlog } = useBlog()

  useEffect(() => {
    if (id) fetchBlog(id)
  }, [id])

  return (
    <AdminLayout>
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
                  <TableCell>{post.state}</TableCell>
                  <TableCell>{new Date(post.created_at).toLocaleDateString()}</TableCell>
                  <TableCell>{new Date(post.updated_at).toLocaleDateString()}</TableCell>
                  <TableCell>
                    <IconButton aria-label="view">
                      <VisibilityIcon />
                    </IconButton>
                    <IconButton aria-label="edit" onClick={() => navigate(`/admin/posts/${post.id}/edit`)}>
                      <EditIcon />
                    </IconButton>
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
    </AdminLayout>
  )
}
