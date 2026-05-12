import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useUsers } from '../useUsers'
import type { User } from '../../../dtos/User'

vi.mock('@auth0/auth0-react', () => ({
  useAuth0: () => ({
    getAccessTokenSilently: vi.fn().mockResolvedValue('test-token'),
  }),
}))

const mockUsers: User[] = [
  {
    id: 'user-1',
    auth0_id: 'auth0|abc123',
    email: 'user1@example.com',
    email_verified: true,
    name: 'User One',
    picture: 'https://example.com/user1.jpg',
    created_at: '2024-01-01T00:00:00.000Z',
    updated_at: '2024-01-02T00:00:00.000Z',
  },
  {
    id: 'user-2',
    auth0_id: 'auth0|def456',
    email: 'user2@example.com',
    email_verified: false,
    name: 'User Two',
    picture: null,
    created_at: '2024-02-01T00:00:00.000Z',
    updated_at: '2024-02-02T00:00:00.000Z',
  },
]

function makeFetchResponse(body: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: () => Promise.resolve(body),
  } as unknown as Response
}

beforeEach(() => {
  vi.stubGlobal('fetch', vi.fn())
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('useUsers (admin)', () => {
  it('initializes with loading=true, users=[], error=null', () => {
    const { result } = renderHook(() => useUsers())
    expect(result.current.loading).toBe(true)
    expect(result.current.users).toEqual([])
    expect(result.current.error).toBeNull()
  })

  it('exposes a fetchUsers function', () => {
    const { result } = renderHook(() => useUsers())
    expect(typeof result.current.fetchUsers).toBe('function')
  })

  it('sets users and clears loading on successful fetch', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockUsers))

    const { result } = renderHook(() => useUsers())

    await act(async () => {
      result.current.fetchUsers()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.users).toEqual(mockUsers)
    expect(result.current.error).toBeNull()
  })

  it('calls fetch with the correct admin URL (/admin/users)', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockUsers))

    const { result } = renderHook(() => useUsers())

    await act(async () => {
      result.current.fetchUsers()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(fetch).toHaveBeenCalledWith('/admin/users', {
      headers: { Authorization: 'Bearer test-token' },
    })
  })

  it('includes the Authorization header with the bearer token', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockUsers))

    const { result } = renderHook(() => useUsers())

    await act(async () => {
      result.current.fetchUsers()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    const [, options] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
    expect((options.headers as Record<string, string>)['Authorization']).toBe('Bearer test-token')
  })

  it('sets error and clears loading when server returns a non-OK status', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(null, false, 401))

    const { result } = renderHook(() => useUsers())

    await act(async () => {
      result.current.fetchUsers()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.users).toEqual([])
    expect(result.current.error).toBe('Server returned 401')
  })

  it('sets error and clears loading when fetch throws a network error', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network failure'))

    const { result } = renderHook(() => useUsers())

    await act(async () => {
      result.current.fetchUsers()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.users).toEqual([])
    expect(result.current.error).toBe('Network failure')
  })

  it('resets loading and error state before each fetchUsers call', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(null, false, 500))

    const { result } = renderHook(() => useUsers())

    await act(async () => {
      result.current.fetchUsers()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toBeTruthy()

    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockUsers))

    await act(async () => {
      result.current.fetchUsers()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.users).toEqual(mockUsers)
    expect(result.current.error).toBeNull()
  })
})
