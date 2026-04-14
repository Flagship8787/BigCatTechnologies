import { useState } from 'react'
import {
  TextField,
  Button,
  Box,
  Stack,
} from '@mui/material'
import RichTextEditor from './RichTextEditor'

interface PostFormValues {
  title: string
  body: string
  state: string
}

interface PostFormProps {
  initialValues?: PostFormValues
  onSubmit: (values: PostFormValues) => Promise<void>
  submitLabel?: string
  onCancel?: () => void
  loading?: boolean
}

export default function PostForm({
  initialValues,
  onSubmit,
  submitLabel = 'Save Post',
  onCancel,
  loading = false,
}: PostFormProps) {
  const [title, setTitle] = useState(initialValues?.title ?? '')
  const [body, setBody] = useState(initialValues?.body ?? '')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    await onSubmit({ title, body, state: initialValues?.state ?? 'drafted' })
  }

  return (
    <Box component="form" onSubmit={handleSubmit} noValidate>
      <Stack spacing={3}>
        <TextField
          label="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
          fullWidth
        />
        <RichTextEditor value={body} onChange={(html) => setBody(html)} />
        <Stack direction="row" spacing={2}>
          <Button type="submit" variant="contained" disabled={loading}>
            {submitLabel}
          </Button>
          {onCancel && (
            <Button variant="outlined" onClick={onCancel} disabled={loading}>
              Cancel
            </Button>
          )}
        </Stack>
      </Stack>
    </Box>
  )
}
