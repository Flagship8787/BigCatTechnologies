import { useEffect, useState } from 'react'
import { useAuth0 } from '@auth0/auth0-react'
import { Box, Chip, CircularProgress, Paper, Typography } from '@mui/material'
import { PageContainer } from '@toolpad/core/PageContainer'
import './Dashboard.css'

function decodeJwtPayload(token: string): Record<string, unknown> {
  const payload = token.split('.')[1]
  return JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
}

export default function Dashboard() {
  const { user, getAccessTokenSilently } = useAuth0()
  const [permissions, setPermissions] = useState<string[] | null>(null)

  useEffect(() => {
    getAccessTokenSilently()
      .then((token) => {
        const payload = decodeJwtPayload(token)
        const perms = payload.permissions
        setPermissions(Array.isArray(perms) ? perms : [])
      })
      .catch(() => setPermissions([]))
  }, [getAccessTokenSilently])

  return (
    <PageContainer title="Dashboard">
      <section>
        <h1>Dashboard</h1>
        <p>Welcome back, {user?.email}</p>
      </section>

      <section>
        <p>You are authenticated. This is a protected area of the site.</p>
        {user?.picture && (
          <img
            src={user.picture}
            alt={user.name ?? 'Profile'}
            className="dashboard-avatar"
          />
        )}
        <p><strong>Name:</strong> {user?.name}</p>
        <p><strong>Email:</strong> {user?.email}</p>
      </section>

      <Paper variant="outlined" sx={{ p: 2, mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          Permissions
        </Typography>
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
      </Paper>
    </PageContainer>
  )
}
