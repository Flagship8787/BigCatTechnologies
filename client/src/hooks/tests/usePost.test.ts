import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { usePost } from '../usePost'
import type { Post } from '../../dtos/Post'

const mockPost: Post = {
  id: 'post-123',
  blog_id: 'blog-abc',
  title: 'Hello World',
  body: 'This is the post body.',
  created_at: '2024-06-15T10:00:00.000Z',
  updated_at: '2024-06-15T12:00:00.000Z',
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

describe('usePost', () => {
  it('initializes with loading=true, post=null, error=null', () => {
    const { result } = renderHook(() => usePost())
    expect(result.current.loading).toBe(true)
    expect(result.current.post).toBeNull()
    expect(result.current.error).toBeNull()
  })

  it('exposes a fetchPost function', () => {
    const { result } = renderHook(() => usePost())
    expect(typeof result.current.fetchPost).toBe('function')
  })

  it('sets post and clears loading on successful fetch', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockPost))

    const { result } = renderHook(() => usePost())

    await act(async () => {
      result.current.fetchPost('post-123')
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.post).toEqual(mockPost)
    expect(result.current.error).toBeNull()
  })

  it('calls fetch with the correct URL', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockPost))

    const { result } = renderHook(() => usePost())

    await act(async () => {
      result.current.fetchPost('post-123')
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(fetch).toHaveBeenCalledWith('/posts/post-123')
  })

  it('sets error and clears loading when server returns a non-OK status', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(null, false, 404))

    const { result } = renderHook(() => usePost())

    await act(async () => {
      result.current.fetchPost('post-missing')
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.post).toBeNull()
    expect(result.current.error).toBe('Server returned 404')
  })

  it('sets error and clears loading when fetch throws a network error', async () => {
    vi.mocked(fetch).mockRejectedValueOnce(new Error('Network failure'))

    const { result } = renderHook(() => usePost())

    await act(async () => {
      result.current.fetchPost('post-123')
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.post).toBeNull()
    expect(result.current.error).toBe('Network failure')
  })

  it('resets loading and error state before each fetchPost call', async () => {
    // First call: error
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(null, false, 500))

    const { result } = renderHook(() => usePost())

    await act(async () => {
      result.current.fetchPost('post-123')
    })

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toBeTruthy()

    // Second call: success — loading should reset to true mid-flight
    vi.mocked(fetch).mockResolvedValueOnce(makeFetchResponse(mockPost))

    await act(async () => {
      result.current.fetchPost('post-123')
    })

    await waitFor(() => expect(result.current.loading).toBe(false))

    expect(result.current.post).toEqual(mockPost)
    expect(result.current.error).toBeNull()
  })
})
