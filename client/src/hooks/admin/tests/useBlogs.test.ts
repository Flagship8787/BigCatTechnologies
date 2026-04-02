import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useBlogs } from '../useBlogs'
import type { Blog } from '../../../dtos/Blog'

vi.mock('@auth0/auth0-react', () => ({
  useAuth0: () => ({
    getAccessTokenSilently: vi.fn().mockResolvedValue('test-token'),
  }),
}))

const mockBlogs: Blog[] = [
  {
    id: 'blog-1',
    name: 'First Blog',
    description: 'A test blog',
    created_at: '2024-01-01T00:00:00.000Z',
    updated_at: '2024-01-02T00:00:00.000Z',
  },
  {
    id: 'blog-2',
    name: 'Second Blog',
    description: 'Another test blog',
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

describe('useBlogs (admin)', () => {
  it('initializes with loading=true, blogs=[], error=null', () => {
    const { result } = renderHook(() => useBlogs())
    expect(result.current.loading).toBe(true)
    expect(result.current.blogs).toEqual([])
    expect(result.current.error).toBeNull()
  })

  it('exposes a fetchBlogs function', () => {
    const { result } = renderHook(() => useBlogs())
    expect(typeof result.current.fetchBlogs).toBe('function')
  })

  it('sets blogs and clears loading on successful fetch', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockBlogs))

    const { result } = renderHook(() => useBlogs())

    await act(async () => {
      result.current.fetchBlogs()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.blogs).toEqual(mockBlogs)
    expect(result.current.error).toBeNull()
  })

  it('calls fetch with the correct admin URL', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockBlogs))

    const { result } = renderHook(() => useBlogs())

    await act(async () => {
      result.current.fetchBlogs()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(fetch).toHaveBeenCalledWith('/admin/blogs', {
      headers: { Authorization: 'Bearer test-token' },
    })
  })

  it('includes the Authorization header with the bearer token', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockBlogs))

    const { result } = renderHook(() => useBlogs())

    await act(async () => {
      result.current.fetchBlogs()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    const [, options] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
    expect((options.headers as Record<string, string>)['Authorization']).toBe('Bearer test-token')
  })

  it('sets error and clears loading when server returns a non-OK status', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(null, false, 401))

    const { result } = renderHook(() => useBlogs())

    await act(async () => {
      result.current.fetchBlogs()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.blogs).toEqual([])
    expect(result.current.error).toBe('Server returned 401')
  })

  it('sets error and clears loading when fetch throws a network error', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network failure'))

    const { result } = renderHook(() => useBlogs())

    await act(async () => {
      result.current.fetchBlogs()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.blogs).toEqual([])
    expect(result.current.error).toBe('Network failure')
  })

  it('resets loading and error state before each fetchBlogs call', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(null, false, 500))

    const { result } = renderHook(() => useBlogs())

    await act(async () => {
      result.current.fetchBlogs()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toBeTruthy()

    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockBlogs))

    await act(async () => {
      result.current.fetchBlogs()
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.blogs).toEqual(mockBlogs)
    expect(result.current.error).toBeNull()
  })
})
