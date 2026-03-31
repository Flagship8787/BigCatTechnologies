import { useState } from 'react'
import {
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Button,
  Box,
  Stack,
} from '@mui/material'

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
  const [state, setState] = useState(initialValues?.state ?? 'drafted')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    await onSubmit({ title, body, state })
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
        <TextField
          label="Body"
          value={body}
          onChange={(e) => setBody(e.target.value)}
          multiline
          minRows={8}
          fullWidth
        />
        <FormControl fullWidth>
          <InputLabel id="state-label">State</InputLabel>
          <Select
            labelId="state-label"
            value={state}
            label="State"
            onChange={(e) => setState(e.target.value)}
          >
            <MenuItem value="drafted">drafted</MenuItem>
            <MenuItem value="published">published</MenuItem>
            <MenuItem value="deleted">deleted</MenuItem>
          </Select>
        </FormControl>
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
