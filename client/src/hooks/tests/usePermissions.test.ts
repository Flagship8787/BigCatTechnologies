import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { usePermissions } from '../usePermissions'

// Build a minimal fake JWT with the given permissions
function makeJwt(permissions: string[]): string {
  const payload = btoa(JSON.stringify({ sub: 'user-1', permissions }))
  return `header.${payload}.signature`
}

const mockGetAccessTokenSilently = vi.fn()
const mockIsAuthenticated = { value: true }

vi.mock('@auth0/auth0-react', () => ({
  useAuth0: () => ({
    isAuthenticated: mockIsAuthenticated.value,
    getAccessTokenSilently: mockGetAccessTokenSilently,
  }),
}))

beforeEach(() => {
  mockIsAuthenticated.value = true
  mockGetAccessTokenSilently.mockReset()
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('usePermissions', () => {
  it('starts with permissions=null (loading state)', () => {
    mockGetAccessTokenSilently.mockReturnValue(new Promise(() => {})) // never resolves

    const { result } = renderHook(() => usePermissions())

    expect(result.current.permissions).toBeNull()
    expect(result.current.isLoading).toBe(true)
  })

  it('returns empty array when not authenticated', async () => {
    mockIsAuthenticated.value = false

    const { result } = renderHook(() => usePermissions())

    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.permissions).toEqual([])
  })

  it('returns permissions from JWT when authenticated', async () => {
    const perms = ['admin', 'posts:admin']
    mockGetAccessTokenSilently.mockResolvedValue(makeJwt(perms))

    const { result } = renderHook(() => usePermissions())

    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.permissions).toEqual(perms)
  })

  it('returns empty array when JWT has no permissions field', async () => {
    const payload = btoa(JSON.stringify({ sub: 'user-1' })) // no permissions key
    mockGetAccessTokenSilently.mockResolvedValue(`header.${payload}.signature`)

    const { result } = renderHook(() => usePermissions())

    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.permissions).toEqual([])
  })

  it('returns empty array when getAccessTokenSilently rejects', async () => {
    mockGetAccessTokenSilently.mockRejectedValue(new Error('token error'))

    const { result } = renderHook(() => usePermissions())

    await waitFor(() => expect(result.current.isLoading).toBe(false))
    expect(result.current.permissions).toEqual([])
  })
})
