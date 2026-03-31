import { useAuth0 } from '@auth0/auth0-react'
import AdminLayout from '../layouts/AdminLayout'

export default function Dashboard() {
  const { user } = useAuth0()

  return (
    <AdminLayout>
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
    </AdminLayout>
  )
}
