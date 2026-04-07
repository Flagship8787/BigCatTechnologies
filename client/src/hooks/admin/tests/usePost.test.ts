import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { usePost } from '../usePost'
import type { Post } from '../../../dtos/Post'

vi.mock('@auth0/auth0-react', () => ({
  useAuth0: () => ({
    getAccessTokenSilently: vi.fn().mockResolvedValue('test-token'),
  }),
}))

const mockPost: Post = {
  id: 'post-123',
  blog_id: 'blog-abc',
  title: 'Hello World',
  body: 'This is the post body.',
  state: 'drafted',
  created_at: '2024-06-15T10:00:00.000Z',
  updated_at: '2024-06-15T12:00:00.000Z',
}

const publishedPost: Post = { ...mockPost, state: 'published' }
const updatedPost: Post = { ...mockPost, title: 'Updated Title', body: 'Updated body.' }

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

describe('usePost (admin)', () => {
  // --- initialization ---

  it('initializes with loading=true, post=null, error=null', () => {
    const { result } = renderHook(() => usePost())
    expect(result.current.loading).toBe(true)
    expect(result.current.post).toBeNull()
    expect(result.current.error).toBeNull()
  })

  it('exposes fetchData, publish, and update functions', () => {
    const { result } = renderHook(() => usePost())
    expect(typeof result.current.fetchData).toBe('function')
    expect(typeof result.current.publish).toBe('function')
    expect(typeof result.current.update).toBe('function')
  })

  // --- fetchData ---

  describe('fetchData', () => {
    it('sets post and clears loading on success', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockPost))

      const { result } = renderHook(() => usePost())

      await act(async () => { result.current.fetchData('post-123') })
      await waitFor(() => expect(result.current.loading).toBe(false))

      expect(result.current.post).toEqual(mockPost)
      expect(result.current.error).toBeNull()
    })

    it('calls fetch with the correct URL and auth header', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockPost))

      const { result } = renderHook(() => usePost())

      await act(async () => { result.current.fetchData('post-123') })
      await waitFor(() => expect(result.current.loading).toBe(false))

      expect(fetch).toHaveBeenCalledWith('/admin/posts/post-123', {
        headers: { Authorization: 'Bearer test-token' },
      })
    })

    it('sets error when server returns non-OK status', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(null, false, 404))

      const { result } = renderHook(() => usePost())

      await act(async () => { result.current.fetchData('post-missing') })
      await waitFor(() => expect(result.current.loading).toBe(false))

      expect(result.current.post).toBeNull()
      expect(result.current.error).toBe('Server returned 404')
    })

    it('sets error on network failure', async () => {
      vi.mocked(fetch).mockRejectedValueOnce(new Error('Network failure'))

      const { result } = renderHook(() => usePost())

      await act(async () => { result.current.fetchData('post-123') })
      await waitFor(() => expect(result.current.loading).toBe(false))

      expect(result.current.post).toBeNull()
      expect(result.current.error).toBe('Network failure')
    })

    it('resets loading and error before each call', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(null, false, 500))

      const { result } = renderHook(() => usePost())

      await act(async () => { result.current.fetchData('post-123') })
      await waitFor(() => expect(result.current.loading).toBe(false))
      expect(result.current.error).toBeTruthy()

      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockPost))

      await act(async () => { result.current.fetchData('post-123') })
      await waitFor(() => expect(result.current.loading).toBe(false))

      expect(result.current.post).toEqual(mockPost)
      expect(result.current.error).toBeNull()
    })
  })

  // --- publish ---

  describe('publish', () => {
    it('calls POST /admin/posts/:postId/publish with auth header', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(publishedPost))

      const { result } = renderHook(() => usePost())

      await act(async () => { await result.current.publish('post-123') })

      expect(fetch).toHaveBeenCalledWith('/admin/posts/post-123/publish', {
        method: 'POST',
        headers: { Authorization: 'Bearer test-token' },
      })
    })

    it('returns the updated post on success', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(publishedPost))

      const { result } = renderHook(() => usePost())

      let returned: Post | undefined
      await act(async () => {
        returned = await result.current.publish('post-123')
      })

      expect(returned).toEqual(publishedPost)
    })

    it('updates post state in hook after successful publish', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(publishedPost))

      const { result } = renderHook(() => usePost())

      await act(async () => { await result.current.publish('post-123') })

      expect(result.current.post).toEqual(publishedPost)
    })

    it('throws with server detail message on non-OK response', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(
        makeFetchResponse({ detail: 'Post must be in drafted state to publish' }, false, 422)
      )

      const { result } = renderHook(() => usePost())

      await expect(
        act(async () => { await result.current.publish('post-123') })
      ).rejects.toThrow('Post must be in drafted state to publish')
    })

    it('throws with generic message when response body has no detail', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse({}, false, 500))

      const { result } = renderHook(() => usePost())

      await expect(
        act(async () => { await result.current.publish('post-123') })
      ).rejects.toThrow('Server returned 500')
    })
  })

  // --- update ---

  describe('update', () => {
    const updateValues = { title: 'Updated Title', body: 'Updated body.', state: 'drafted' }

    it('calls PATCH /admin/posts/:postId with auth header and body', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(updatedPost))

      const { result } = renderHook(() => usePost())

      await act(async () => { await result.current.update('post-123', updateValues) })

      expect(fetch).toHaveBeenCalledWith('/admin/posts/post-123', {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: 'Bearer test-token',
        },
        body: JSON.stringify(updateValues),
      })
    })

    it('returns the updated post on success', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(updatedPost))

      const { result } = renderHook(() => usePost())

      let returned: Post | undefined
      await act(async () => {
        returned = await result.current.update('post-123', updateValues)
      })

      expect(returned).toEqual(updatedPost)
    })

    it('updates post state in hook after successful update', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(updatedPost))

      const { result } = renderHook(() => usePost())

      await act(async () => { await result.current.update('post-123', updateValues) })

      expect(result.current.post).toEqual(updatedPost)
    })

    it('throws with server detail message on non-OK response', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(
        makeFetchResponse({ detail: "title must not be blank" }, false, 422)
      )

      const { result } = renderHook(() => usePost())

      await expect(
        act(async () => { await result.current.update('post-123', updateValues) })
      ).rejects.toThrow('title must not be blank')
    })

    it('throws with generic message when response body has no detail', async () => {
      vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse({}, false, 500))

      const { result } = renderHook(() => usePost())

      await expect(
        act(async () => { await result.current.update('post-123', updateValues) })
      ).rejects.toThrow('Server returned 500')
    })
  })
})
