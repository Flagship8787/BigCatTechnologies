import type { ReactNode } from 'react'
import { Alert, Box, CircularProgress } from '@mui/material'
import { usePermissions } from '../hooks/usePermissions'

const ADMIN_PERMISSIONS = ['admin', 'posts:admin', 'posts:admin:own', 'posts:create']

interface Props {
  children: ReactNode
}

export default function AdminGuard({ children }: Props) {
  const { permissions, isLoading } = usePermissions()

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
        <CircularProgress />
      </Box>
    )
  }

  const hasAdminAccess = permissions?.some((p) => ADMIN_PERMISSIONS.includes(p)) ?? false

  if (!hasAdminAccess) {
    return (
      <Box sx={{ maxWidth: 600, mx: 'auto', mt: 8, px: 3 }}>
        <Alert severity="warning">
          Admin functionality is not enabled for this user account. Please contact{' '}
          <a href="mailto:samshapiro87.agent@gmail.com">samshapiro87.agent@gmail.com</a> if you
          believe you are receiving this message in error.
        </Alert>
      </Box>
    )
  }

  return <>{children}</>
}
