import { useEffect, useState, useCallback } from 'react'
import { useNavigate, Link as RouterLink } from 'react-router-dom'
import { useAuth0 } from '@auth0/auth0-react'
import {
  Box,
  Button,
  Chip,
  CircularProgress,
  Link,
  List,
  ListItem,
  ListItemText,
  Paper,
  Stack,
  Tooltip,
  Typography,
} from '@mui/material'
import { PageContainer } from '@toolpad/core/PageContainer'
import AddIcon from '@mui/icons-material/Add'
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline'
import PublishIcon from '@mui/icons-material/Publish'
import { useBlogs } from '../../hooks/admin/useBlogs'
import { usePost } from '../../hooks/admin/usePost'
import { useMarkdown } from '../../hooks/useMarkdown'
import type { BlogWithPosts } from '../../dtos/Blog'
import type { Post } from '../../dtos/Post'

const API_URL = import.meta.env.VITE_API_URL ?? ''

function formatRelative(dateStr: string): string {
  const now = Date.now()
  const then = new Date(dateStr).getTime()
  const diffMs = now - then
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d ago`
}

export default function Dashboard() {
  const navigate = useNavigate()
  const { getAccessTokenSilently, user } = useAuth0()
  const { strip } = useMarkdown()
  const { blogs, fetchBlogs } = useBlogs()
  const { publish } = usePost()

  const [permissions, setPermissions] = useState<string[] | null>(null)
  const [posts, setPosts] = useState<Post[]>([])
  const [blogMap, setBlogMap] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [publishingId, setPublishingId] = useState<string | null>(null)

  function decodeJwtPayload(token: string): Record<string, unknown> {
    const payload = token.split('.')[1]
    return JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
  }

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const token = await getAccessTokenSilently()

      // Decode permissions from JWT
      const payload = decodeJwtPayload(token)
      const perms = payload.permissions
      setPermissions(Array.isArray(perms) ? perms : [])

      // Fetch all blogs via hook
      await fetchBlogs()

      // Fetch posts for each blog (need BlogWithPosts)
      const blogWithPostsResults = await Promise.all(
        blogs.map((blog) =>
          fetch(`${API_URL}/admin/blogs/${blog.id}`, {
            headers: { Authorization: `Bearer ${token}` },
          })
            .then((r) => (r.ok ? r.json() as Promise<BlogWithPosts> : null))
            .catch(() => null)
        )
      )

      const newBlogMap: Record<string, string> = {}
      const allPosts: Post[] = []
      for (const result of blogWithPostsResults) {
        if (result) {
          newBlogMap[result.id] = result.name
          allPosts.push(...result.posts)
        }
      }

      setBlogMap(newBlogMap)
      setPosts(allPosts)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }, [getAccessTokenSilently, fetchBlogs, blogs])

  useEffect(() => {
    void fetchData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handlePublish = useCallback(async (postId: string) => {
    setPublishingId(postId)
    try {
      await publish(postId)
      await fetchData()
    } catch (err) {
      console.error('Publish failed:', err)
    } finally {
      setPublishingId(null)
    }
  }, [publish, fetchData])

  if (loading) {
    return (
      <PageContainer title="Dashboard">
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
          <CircularProgress />
        </Box>
      </PageContainer>
    )
  }

  if (error) {
    return (
      <PageContainer title="Dashboard">
        <Typography color="error">{error}</Typography>
      </PageContainer>
    )
  }

  const draftCount = posts.filter((p) => p.state === 'drafted').length
  const publishedCount = posts.filter((p) => p.state === 'published').length
  const recentPosts = [...posts].sort(
    (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
  ).slice(0, 10)

  return (
    <PageContainer title="Dashboard">
      {/* Stats Row */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: 'repeat(4, 1fr)',
          gap: '14px',
          mb: '24px',
        }}
      >
        {/* Drafts Pending — featured */}
        <Paper
          sx={{
            p: '18px 20px',
            border: '1px solid',
            borderColor: 'primary.main',
            backgroundColor: 'primary.light',
            borderRadius: 2.5,
          }}
        >
          <Typography variant="overline" sx={{ color: 'primary.dark', letterSpacing: '0.06em' }}>
            Drafts Pending
          </Typography>
          <Typography variant="h3" sx={{ fontWeight: 300, color: 'primary.dark', lineHeight: 1, mt: 0.5 }}>
            {draftCount}
          </Typography>
          <Typography variant="caption" sx={{ color: 'primary.dark', opacity: 0.7 }}>
            waiting to publish
          </Typography>
        </Paper>

        {/* Published Posts */}
        <Paper variant="outlined" sx={{ p: '18px 20px', borderRadius: 2.5 }}>
          <Typography variant="overline" color="text.secondary">Published Posts</Typography>
          <Typography variant="h3" sx={{ fontWeight: 300, lineHeight: 1, mt: 0.5 }}>{publishedCount}</Typography>
          <Typography variant="caption" color="text.secondary">across all blogs</Typography>
        </Paper>

        {/* Total Posts */}
        <Paper variant="outlined" sx={{ p: '18px 20px', borderRadius: 2.5 }}>
          <Typography variant="overline" color="text.secondary">Total Posts</Typography>
          <Typography variant="h3" sx={{ fontWeight: 300, lineHeight: 1, mt: 0.5 }}>{posts.length}</Typography>
          <Typography variant="caption" color="text.secondary">all time</Typography>
        </Paper>

        {/* Blogs */}
        <Paper variant="outlined" sx={{ p: '18px 20px', borderRadius: 2.5 }}>
          <Typography variant="overline" color="text.secondary">Blogs</Typography>
          <Typography variant="h3" sx={{ fontWeight: 300, lineHeight: 1, mt: 0.5 }}>{blogs.length}</Typography>
          <Typography variant="caption" color="text.secondary">active</Typography>
        </Paper>
      </Box>

      {/* Dashboard Grid */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: '1fr 340px',
          gap: '20px',
          alignItems: 'start',
        }}
      >
        {/* Left — Recent Posts */}
        <Paper variant="outlined">
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              p: '16px 20px 12px',
              borderBottom: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Typography variant="subtitle2" fontWeight={600}>
              Recent Posts
            </Typography>
            <Link component={RouterLink} to="/admin/blogs" variant="body2">
              View all →
            </Link>
          </Box>

          {recentPosts.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ p: 3 }}>
              No posts yet.
            </Typography>
          ) : (
            <List disablePadding>
              {recentPosts.map((post, idx) => {
                const isPublished = post.state === 'published'
                const preview = strip(post.body).slice(0, 200)
                const blogName = blogMap[post.blog_id] ?? 'Unknown'

                return (
                  <Tooltip
                    key={post.id}
                    placement="bottom-start"
                    title={
                      <Box sx={{ p: 0.5, maxWidth: 320 }}>
                        <Typography variant="subtitle2">{post.title}</Typography>
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                          {preview || '(no content)'}
                        </Typography>
                      </Box>
                    }
                    componentsProps={{
                      tooltip: {
                        sx: {
                          bgcolor: 'background.paper',
                          color: 'text.primary',
                          border: '1px solid',
                          borderColor: 'divider',
                          boxShadow: 3,
                          borderRadius: 2,
                        },
                      },
                    }}
                  >
                    <ListItem
                      divider={idx < recentPosts.length - 1}
                      sx={{
                        px: '20px',
                        py: '10px',
                        gap: 1.5,
                        '&:hover .post-actions': { opacity: 1 },
                      }}
                    >
                      {/* Status dot */}
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          flexShrink: 0,
                          bgcolor: isPublished ? 'success.main' : 'warning.main',
                        }}
                      />

                      <ListItemText
                        primary={
                          <Typography
                            variant="body2"
                            fontWeight={500}
                            sx={{
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {post.title}
                          </Typography>
                        }
                        secondary={
                          <Box
                            component="span"
                            sx={{ display: 'flex', alignItems: 'center', gap: 0.75, mt: 0.25, flexWrap: 'wrap' }}
                          >
                            <Chip
                              label={post.state}
                              size="small"
                              sx={{
                                height: 18,
                                fontSize: '0.65rem',
                                bgcolor: isPublished ? 'success.main' : 'warning.main',
                                color: '#fff',
                              }}
                            />
                            <Typography variant="caption" color="text.secondary">{blogName}</Typography>
                            <Typography variant="caption" color="text.secondary">·</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {formatRelative(post.updated_at)}
                            </Typography>
                          </Box>
                        }
                      />

                      {/* Action buttons — appear on hover */}
                      <Stack
                        className="post-actions"
                        direction="row"
                        spacing={0.75}
                        sx={{ opacity: 0, transition: 'opacity 0.15s', flexShrink: 0 }}
                      >
                        {!isPublished && (
                          <Button
                            variant="contained"
                            size="small"
                            disabled={publishingId === post.id}
                            onClick={() => void handlePublish(post.id)}
                          >
                            {publishingId === post.id ? <CircularProgress size={14} color="inherit" /> : 'Publish'}
                          </Button>
                        )}
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => navigate(`/admin/posts/${post.id}/edit`)}
                        >
                          Edit
                        </Button>
                      </Stack>
                    </ListItem>
                  </Tooltip>
                )
              })}
            </List>
          )}
        </Paper>

        {/* Right column */}
        <Stack spacing={2}>
          {/* Quick Actions */}
          <Paper variant="outlined">
            <Box sx={{ p: '12px 16px 8px', borderBottom: '1px solid', borderColor: 'divider' }}>
              <Typography variant="subtitle2" fontWeight={600}>Quick Actions</Typography>
            </Box>
            <Stack spacing={1} sx={{ p: 2 }}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<AddIcon />}
                onClick={() => navigate('/admin/blogs/new')}
              >
                New Post
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<PublishIcon />}
                onClick={() => {
                  const firstDraft = posts.find((p) => p.state === 'drafted')
                  if (firstDraft) void handlePublish(firstDraft.id)
                }}
                disabled={draftCount === 0}
              >
                Publish a Draft
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<AddCircleOutlineIcon />}
                onClick={() => navigate('/admin/blogs/new')}
              >
                Create New Blog
              </Button>
            </Stack>
          </Paper>

          {/* Recent Activity */}
          <Paper variant="outlined">
            <Box sx={{ p: '12px 16px 8px', borderBottom: '1px solid', borderColor: 'divider' }}>
              <Typography variant="subtitle2" fontWeight={600}>Recent Activity</Typography>
            </Box>
            <List dense disablePadding sx={{ px: 1, py: 0.5 }}>
              {recentPosts.slice(0, 6).map((post) => (
                <ListItem key={post.id} sx={{ px: 1, py: 0.75, gap: 1 }}>
                  <Box
                    sx={{
                      width: 6,
                      height: 6,
                      borderRadius: '50%',
                      flexShrink: 0,
                      bgcolor: 'primary.main',
                    }}
                  />
                  <Typography variant="caption" sx={{ flex: 1, minWidth: 0 }}>
                    <strong
                      style={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        display: 'block',
                      }}
                    >
                      {post.title}
                    </strong>
                    {post.state === 'published' ? 'Published' : 'Updated draft'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ flexShrink: 0 }}>
                    {formatRelative(post.updated_at)}
                  </Typography>
                </ListItem>
              ))}
              {recentPosts.length === 0 && (
                <ListItem sx={{ px: 1 }}>
                  <Typography variant="caption" color="text.secondary">No activity yet.</Typography>
                </ListItem>
              )}
            </List>
          </Paper>

          {/* Permissions */}
          <Paper variant="outlined">
            <Box sx={{ p: '12px 16px 8px', borderBottom: '1px solid', borderColor: 'divider' }}>
              <Typography variant="subtitle2" fontWeight={600}>Permissions</Typography>
            </Box>
            <Box sx={{ p: 2 }}>
              {permissions === null ? (
                <CircularProgress size={20} />
              ) : permissions.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  No permissions assigned.
                </Typography>
              ) : (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {permissions.map((perm) => (
                    <Chip key={perm} label={perm} size="small" variant="outlined" />
                  ))}
                </Box>
              )}
            </Box>

            {user && (
              <Box sx={{ p: '0 16px 14px', display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <Box
                  sx={{
                    width: 28,
                    height: 28,
                    borderRadius: '50%',
                    bgcolor: 'primary.dark',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    overflow: 'hidden',
                    flexShrink: 0,
                  }}
                >
                  {user.picture ? (
                    <img src={user.picture} alt={user.name ?? 'User'} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    <Typography variant="caption" sx={{ color: '#fff', fontSize: '0.65rem' }}>
                      {(user.name ?? user.email ?? 'U')[0].toUpperCase()}
                    </Typography>
                  )}
                </Box>
                <Box sx={{ minWidth: 0 }}>
                  <Typography variant="caption" fontWeight={600} sx={{ display: 'block', lineHeight: 1.3 }}>
                    {user.name}
                  </Typography>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}
                  >
                    {user.email}
                  </Typography>
                </Box>
              </Box>
            )}
          </Paper>
        </Stack>
      </Box>
    </PageContainer>
  )
}
