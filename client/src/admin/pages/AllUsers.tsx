import { useEffect } from 'react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  CircularProgress,
  Typography,
  Avatar,
  Chip,
  Box,
} from '@mui/material'
import { PageContainer } from '@toolpad/core/PageContainer'
import { useUsers } from '../../hooks/admin/useUsers'

export default function AllUsers() {
  const { users, error, loading, fetchUsers } = useUsers()

  useEffect(() => {
    fetchUsers()
  }, [])

  return (
    <PageContainer title="All Users">
      {loading && <CircularProgress />}
      {error && <Typography color="error">{error}</Typography>}
      {!loading && !error && (
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Avatar</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Created</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((user) => {
              const initials = (user.name ?? user.email ?? '?')[0].toUpperCase()
              return (
                <TableRow key={user.id}>
                  <TableCell>
                    {user.picture ? (
                      <Avatar src={user.picture} sx={{ width: 32, height: 32 }} />
                    ) : (
                      <Avatar sx={{ width: 32, height: 32, fontSize: 14 }}>{initials}</Avatar>
                    )}
                  </TableCell>
                  <TableCell>{user.name ?? '—'}</TableCell>
                  <TableCell>
                    {user.email ? (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <span>{user.email}</span>
                        {user.email_verified ? (
                          <Chip label="Verified" color="success" size="small" />
                        ) : (
                          <Chip label="Unverified" color="warning" size="small" />
                        )}
                      </Box>
                    ) : (
                      '—'
                    )}
                  </TableCell>
                  <TableCell>{new Date(user.created_at).toLocaleDateString()}</TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      )}
    </PageContainer>
  )
}
