import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import Underline from '@tiptap/extension-underline'
import TextAlign from '@tiptap/extension-text-align'
import Placeholder from '@tiptap/extension-placeholder'
import { Box, IconButton, Divider, Paper, Typography } from '@mui/material'
import FormatBoldIcon from '@mui/icons-material/FormatBold'
import FormatItalicIcon from '@mui/icons-material/FormatItalic'
import FormatUnderlinedIcon from '@mui/icons-material/FormatUnderlined'
import FormatListBulletedIcon from '@mui/icons-material/FormatListBulleted'
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered'
import LinkIcon from '@mui/icons-material/Link'
import './RichTextEditor.css'

interface RichTextEditorProps {
  value: string
  onChange: (html: string) => void
}

export default function RichTextEditor({ value, onChange }: RichTextEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Link.configure({ openOnClick: false }),
      Underline,
      TextAlign.configure({ types: ['heading', 'paragraph'] }),
      Placeholder.configure({ placeholder: 'Write your post…' }),
    ],
    content: value,
    onUpdate({ editor }) {
      onChange(editor.getHTML())
    },
  })

  if (!editor) return null

  function handleLink() {
    const url = window.prompt('Enter URL')
    if (!url) return
    editor!.chain().focus().setLink({ href: url }).run()
  }

  const btnSx = (active: boolean) => ({
    borderRadius: 1,
    bgcolor: active ? 'action.selected' : undefined,
  })

  return (
    <Paper variant="outlined">
      <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 0.5, p: 0.75, borderBottom: '1px solid', borderColor: 'divider' }}>
        <IconButton size="small" onClick={() => editor.chain().focus().toggleBold().run()} sx={btnSx(editor.isActive('bold'))}>
          <FormatBoldIcon fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={() => editor.chain().focus().toggleItalic().run()} sx={btnSx(editor.isActive('italic'))}>
          <FormatItalicIcon fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={() => editor.chain().focus().toggleUnderline().run()} sx={btnSx(editor.isActive('underline'))}>
          <FormatUnderlinedIcon fontSize="small" />
        </IconButton>
        <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
        <IconButton
          size="small"
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          sx={btnSx(editor.isActive('heading', { level: 2 }))}
        >
          <Typography variant="caption" fontWeight="bold" lineHeight={1}>H2</Typography>
        </IconButton>
        <IconButton
          size="small"
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          sx={btnSx(editor.isActive('heading', { level: 3 }))}
        >
          <Typography variant="caption" fontWeight="bold" lineHeight={1}>H3</Typography>
        </IconButton>
        <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
        <IconButton size="small" onClick={() => editor.chain().focus().toggleBulletList().run()} sx={btnSx(editor.isActive('bulletList'))}>
          <FormatListBulletedIcon fontSize="small" />
        </IconButton>
        <IconButton size="small" onClick={() => editor.chain().focus().toggleOrderedList().run()} sx={btnSx(editor.isActive('orderedList'))}>
          <FormatListNumberedIcon fontSize="small" />
        </IconButton>
        <Divider orientation="vertical" flexItem sx={{ mx: 0.5 }} />
        <IconButton size="small" onClick={handleLink} sx={btnSx(editor.isActive('link'))}>
          <LinkIcon fontSize="small" />
        </IconButton>
      </Box>
      <Box className="rich-text-editor-content">
        <EditorContent editor={editor} />
      </Box>
    </Paper>
  )
}
