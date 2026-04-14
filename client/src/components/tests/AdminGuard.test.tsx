import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'

const mockUsePermissions = vi.fn()

vi.mock('../../hooks/usePermissions', () => ({
  usePermissions: () => mockUsePermissions(),
}))

// Import after mock is set up
import AdminGuard from '../AdminGuard'

function setPermissions(permissions: string[]) {
  mockUsePermissions.mockReturnValue({ permissions, isLoading: false })
}

beforeEach(() => {
  mockUsePermissions.mockReset()
})

describe('AdminGuard', () => {
  it('shows a spinner while permissions are loading', () => {
    mockUsePermissions.mockReturnValue({ permissions: null, isLoading: true })

    render(
      <AdminGuard>
        <div>Admin content</div>
      </AdminGuard>
    )

    expect(screen.queryByText('Admin content')).not.toBeInTheDocument()
    expect(screen.queryByText(/not enabled/i)).not.toBeInTheDocument()
    // MUI CircularProgress renders an SVG role="progressbar"
    expect(document.querySelector('[role="progressbar"]')).toBeTruthy()
  })

  it('renders children when user has admin permission', () => {
    setPermissions(['admin'])

    render(
      <AdminGuard>
        <div>Admin content</div>
      </AdminGuard>
    )

    expect(screen.getByText('Admin content')).toBeInTheDocument()
  })

  it('renders children when user has posts:admin permission', () => {
    setPermissions(['posts:admin'])

    render(
      <AdminGuard>
        <div>Admin content</div>
      </AdminGuard>
    )

    expect(screen.getByText('Admin content')).toBeInTheDocument()
  })

  it('renders children when user has posts:admin:own permission', () => {
    setPermissions(['posts:admin:own'])

    render(
      <AdminGuard>
        <div>Admin content</div>
      </AdminGuard>
    )

    expect(screen.getByText('Admin content')).toBeInTheDocument()
  })

  it('renders children when user has posts:create permission', () => {
    setPermissions(['posts:create'])

    render(
      <AdminGuard>
        <div>Admin content</div>
      </AdminGuard>
    )

    expect(screen.getByText('Admin content')).toBeInTheDocument()
  })

  it('shows error message when user has no permissions', () => {
    setPermissions([])

    render(
      <AdminGuard>
        <div>Admin content</div>
      </AdminGuard>
    )

    expect(screen.getByText(/Admin functionality is not enabled/i)).toBeInTheDocument()
    expect(screen.getByText('samshapiro87.agent@gmail.com')).toBeInTheDocument()
    expect(screen.queryByText('Admin content')).not.toBeInTheDocument()
  })

  it('shows error message when user has unrecognized permissions only', () => {
    setPermissions(['openid', 'profile', 'read:something'])

    render(
      <AdminGuard>
        <div>Admin content</div>
      </AdminGuard>
    )

    expect(screen.getByText(/Admin functionality is not enabled/i)).toBeInTheDocument()
    expect(screen.queryByText('Admin content')).not.toBeInTheDocument()
  })

  it('renders children when user has one valid permission among others', () => {
    setPermissions(['openid', 'profile', 'posts:admin'])

    render(
      <AdminGuard>
        <div>Admin content</div>
      </AdminGuard>
    )

    expect(screen.getByText('Admin content')).toBeInTheDocument()
    expect(screen.queryByText(/not enabled/i)).not.toBeInTheDocument()
  })
})
