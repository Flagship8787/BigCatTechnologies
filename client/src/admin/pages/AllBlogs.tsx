import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  IconButton,
  CircularProgress,
  Typography,
} from '@mui/material'
import VisibilityIcon from '@mui/icons-material/Visibility'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import AdminLayout from '../layouts/AdminLayout'
import { useBlogs } from '../../hooks/useBlogs'

export default function AllBlogs() {
  const { blogs, error, loading, fetchBlogs } = useBlogs()
  const navigate = useNavigate()

  useEffect(() => {
    fetchBlogs()
  }, [])

  return (
    <AdminLayout>
      <Typography variant="h4" gutterBottom>All Blogs</Typography>
      {loading && <CircularProgress />}
      {error && <Typography color="error">{error}</Typography>}
      {!loading && !error && (
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Description</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Updated</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {blogs.map((blog) => (
              <TableRow key={blog.id}>
                <TableCell>{blog.name}</TableCell>
                <TableCell>{blog.description}</TableCell>
                <TableCell>{new Date(blog.created_at).toLocaleDateString()}</TableCell>
                <TableCell>{new Date(blog.updated_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <IconButton onClick={() => navigate(`/admin/blogs/${blog.id}`)} aria-label="view">
                    <VisibilityIcon />
                  </IconButton>
                  <IconButton aria-label="edit">
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
      )}
    </AdminLayout>
  )
}
