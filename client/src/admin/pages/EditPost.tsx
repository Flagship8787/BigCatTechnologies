import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { CircularProgress, Typography } from '@mui/material'
import PostForm from '../components/PostForm'
import { usePost } from '../../hooks/admin/usePost'

const API_URL = import.meta.env.VITE_API_URL ?? ''

export default function EditPost() {
  const { postId } = useParams<{ postId: string }>()
  const navigate = useNavigate()
  const { post, error: fetchError, loading: fetchLoading, fetchData } = usePost()
  const [submitLoading, setSubmitLoading] = useState(false)
  const [submitError, setSubmitError] = useState<string | null>(null)

  useEffect(() => {
    if (postId) fetchData(postId)
  }, [postId])

  async function handleSubmit(values: { title: string; body: string; state: string }) {
    setSubmitLoading(true)
    setSubmitError(null)
    try {
      const res = await fetch(`${API_URL}/admin/posts/${postId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      })
      if (!res.ok) throw new Error(`Server returned ${res.status}`)
      navigate(`/admin/blogs/${post!.blog_id}`)
    } catch (err) {
      setSubmitError((err as Error).message)
      setSubmitLoading(false)
    }
  }

  return (
    <>
      <Typography variant="h4" gutterBottom>Edit Post</Typography>
      {fetchLoading && <CircularProgress />}
      {fetchError && <Typography color="error">{fetchError}</Typography>}
      {submitError && <Typography color="error" sx={{ mb: 2 }}>{submitError}</Typography>}
      {!fetchLoading && !fetchError && post && (
        <PostForm
          initialValues={{ title: post.title, body: post.body, state: post.state }}
          onSubmit={handleSubmit}
          onCancel={() => navigate(`/admin/blogs/${post.blog_id}`)}
          loading={submitLoading}
        />
      )}
    </>
  )
}
