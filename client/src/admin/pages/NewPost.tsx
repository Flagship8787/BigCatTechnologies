import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Typography } from '@mui/material'
import AdminLayout from '../layouts/AdminLayout'
import PostForm from '../components/PostForm'

const API_URL = import.meta.env.VITE_API_URL ?? ''

export default function NewPost() {
  const { blogId } = useParams<{ blogId: string }>()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(values: { title: string; body: string; state: string }) {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_URL}/blogs/${blogId}/posts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: values.title, body: values.body }),
      })
      if (!res.ok) throw new Error(`Server returned ${res.status}`)
      navigate(`/admin/blogs/${blogId}`)
    } catch (err) {
      setError((err as Error).message)
      setLoading(false)
    }
  }

  return (
    <AdminLayout>
      <Typography variant="h4" gutterBottom>Create New Post</Typography>
      {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}
      <PostForm
        submitLabel="Create Post"
        onSubmit={handleSubmit}
        onCancel={() => navigate(`/admin/blogs/${blogId}`)}
        loading={loading}
      />
    </AdminLayout>
  )
}
