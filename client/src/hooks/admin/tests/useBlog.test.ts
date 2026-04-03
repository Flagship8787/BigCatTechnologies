import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useBlog } from '../useBlog'
import type { BlogWithPosts } from '../../../dtos/Blog'

vi.mock('@auth0/auth0-react', () => ({
  useAuth0: () => ({
    getAccessTokenSilently: vi.fn().mockResolvedValue('test-token'),
  }),
}))

const mockBlog: BlogWithPosts = {
  id: 'blog-abc',
  name: 'Test Blog',
  description: 'A test blog',
  created_at: '2024-01-01T00:00:00.000Z',
  updated_at: '2024-01-02T00:00:00.000Z',
  posts: [
    {
      id: 'post-1',
      blog_id: 'blog-abc',
      title: 'First Post',
      body: 'Post body content.',
      state: 'published',
      created_at: '2024-01-05T00:00:00.000Z',
      updated_at: '2024-01-06T00:00:00.000Z',
    },
  ],
}

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

describe('useBlog (admin)', () => {
  it('initializes with loading=true, blog=null, error=null', () => {
    const { result } = renderHook(() => useBlog())
    expect(result.current.loading).toBe(true)
    expect(result.current.blog).toBeNull()
    expect(result.current.error).toBeNull()
  })

  it('exposes a refreshData function', () => {
    const { result } = renderHook(() => useBlog())
    expect(typeof result.current.refreshData).toBe('function')
  })

  it('exposes a publish function', () => {
    const { result } = renderHook(() => useBlog())
    expect(typeof result.current.publish).toBe('function')
  })

  it('sets blog and clears loading on successful fetch', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockBlog))

    const { result } = renderHook(() => useBlog())

    await act(async () => {
      result.current.refreshData('blog-abc')
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.blog).toEqual(mockBlog)
    expect(result.current.error).toBeNull()
  })

  it('calls fetch with the correct admin URL', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockBlog))

    const { result } = renderHook(() => useBlog())

    await act(async () => {
      result.current.refreshData('blog-abc')
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(fetch).toHaveBeenCalledWith('/admin/blogs/blog-abc', {
      headers: { Authorization: 'Bearer test-token' },
    })
  })

  it('includes the Authorization header with the bearer token', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockBlog))

    const { result } = renderHook(() => useBlog())

    await act(async () => {
      result.current.refreshData('blog-abc')
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    const [, options] = vi.mocked(fetch).mock.calls[0] as [string, RequestInit]
    expect((options.headers as Record<string, string>)['Authorization']).toBe('Bearer test-token')
  })

  it('sets error and clears loading when server returns a non-OK status', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(null, false, 404))

    const { result } = renderHook(() => useBlog())

    await act(async () => {
      result.current.refreshData('blog-missing')
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.blog).toBeNull()
    expect(result.current.error).toBe('Server returned 404')
  })

  it('sets error and clears loading when fetch throws a network error', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network failure'))

    const { result } = renderHook(() => useBlog())

    await act(async () => {
      result.current.refreshData('blog-abc')
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.blog).toBeNull()
    expect(result.current.error).toBe('Network failure')
  })

  it('resets loading and error state before each refreshData call', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(null, false, 500))

    const { result } = renderHook(() => useBlog())

    await act(async () => {
      result.current.refreshData('blog-abc')
    })

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toBeTruthy()

    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockBlog))

    await act(async () => {
      result.current.refreshData('blog-abc')
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.blog).toEqual(mockBlog)
    expect(result.current.error).toBeNull()
  })

  describe('publish', () => {
    it('calls POST /admin/posts/:postId/publish with auth header', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse({}, true, 200))

      const { result } = renderHook(() => useBlog())

      await act(async () => {
        await result.current.publish('post-1')
      })

      expect(fetch).toHaveBeenCalledWith('/admin/posts/post-1/publish', {
        method: 'POST',
        headers: { Authorization: 'Bearer test-token' },
      })
    })

    it('resolves without error on success', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse({}, true, 200))

      const { result } = renderHook(() => useBlog())

      await expect(
        act(async () => {
          await result.current.publish('post-1')
        })
      ).resolves.not.toThrow()
    })

    it('throws when server returns a non-OK status', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(null, false, 422))

      const { result } = renderHook(() => useBlog())

      await expect(
        act(async () => {
          await result.current.publish('post-1')
        })
      ).rejects.toThrow('Server returned 422')
    })
  })
})
