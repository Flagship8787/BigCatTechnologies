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
import { PageContainer } from '@toolpad/core/PageContainer'
import VisibilityIcon from '@mui/icons-material/Visibility'
import EditIcon from '@mui/icons-material/Edit'
import DeleteIcon from '@mui/icons-material/Delete'
import { useBlogs } from '../../hooks/admin/useBlogs'

export default function AllBlogs() {
  const { blogs, error, loading, fetchBlogs } = useBlogs()
  const navigate = useNavigate()

  useEffect(() => {
    fetchBlogs()
  }, [])

  return (
    <PageContainer title="All Blogs">
      {loading && <CircularProgress />}
      {error && <Typography color="error">{error}</Typography>}
      {!loading && !error && (
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Author</TableCell>
              <TableCell>Owner ID</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Updated</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {blogs.map((blog) => (
              <TableRow key={blog.id}>
                <TableCell>{blog.name}</TableCell>
                <TableCell>{blog.author_name}</TableCell>
                <TableCell>{blog.owner_id}</TableCell>
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
    </PageContainer>
  )
}
