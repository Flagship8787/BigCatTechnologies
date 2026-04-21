import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, act, waitFor } from '@testing-library/react'
import { usePosts } from '../usePosts'
import type { Blog } from '../../../dtos/Blog'
import type { BlogWithPosts } from '../../../dtos/Blog'

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
    author_name: 'Test Author',
    owner_id: 'user-123',
    created_at: '2024-01-01T00:00:00.000Z',
    updated_at: '2024-01-02T00:00:00.000Z',
  },
  {
    id: 'blog-2',
    name: 'Second Blog',
    description: 'Another test blog',
    author_name: 'Another Author',
    owner_id: 'user-456',
    created_at: '2024-02-01T00:00:00.000Z',
    updated_at: '2024-02-02T00:00:00.000Z',
  },
]

const mockBlogWithPosts1: BlogWithPosts = {
  ...mockBlogs[0],
  posts: [
    {
      id: 'post-1',
      blog_id: 'blog-1',
      title: 'Post One',
      body: '# Hello\nThis is post one.',
      state: 'published',
      created_at: '2024-01-10T00:00:00.000Z',
      updated_at: '2024-01-11T00:00:00.000Z',
    },
    {
      id: 'post-2',
      blog_id: 'blog-1',
      title: 'Post Two',
      body: 'Draft content',
      state: 'drafted',
      created_at: '2024-01-12T00:00:00.000Z',
      updated_at: '2024-01-13T00:00:00.000Z',
    },
  ],
}

const mockBlogWithPosts2: BlogWithPosts = {
  ...mockBlogs[1],
  posts: [
    {
      id: 'post-3',
      blog_id: 'blog-2',
      title: 'Post Three',
      body: 'Another post',
      state: 'published',
      created_at: '2024-02-10T00:00:00.000Z',
      updated_at: '2024-02-11T00:00:00.000Z',
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

describe('usePosts (admin)', () => {
  it('initializes with loading=false, posts=[], blogMap={}, error=null', () => {
    const { result } = renderHook(() => usePosts())
    expect(result.current.loading).toBe(false)
    expect(result.current.posts).toEqual([])
    expect(result.current.blogMap).toEqual({})
    expect(result.current.error).toBeNull()
  })

  it('exposes a fetchPosts function', () => {
    const { result } = renderHook(() => usePosts())
    expect(typeof result.current.fetchPosts).toBe('function')
  })

  it('returns empty posts and blogMap when called with an empty blogs array', async () => {
    const { result } = renderHook(() => usePosts())
    await act(async () => {
      await result.current.fetchPosts([])
    })
    expect(result.current.posts).toEqual([])
    expect(result.current.blogMap).toEqual({})
    expect(result.current.loading).toBe(false)
  })

  it('fetches posts for each blog and aggregates them', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(makeFetchResponse(mockBlogWithPosts1))
      .mockResolvedValueOnce(makeFetchResponse(mockBlogWithPosts2))
    vi.stubGlobal('fetch', fetchMock)

    const { result } = renderHook(() => usePosts())
    await act(async () => {
      await result.current.fetchPosts(mockBlogs)
    })

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.posts).toHaveLength(3)
    expect(result.current.posts.map((p) => p.id)).toContain('post-1')
    expect(result.current.posts.map((p) => p.id)).toContain('post-2')
    expect(result.current.posts.map((p) => p.id)).toContain('post-3')
  })

  it('builds blogMap correctly', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(makeFetchResponse(mockBlogWithPosts1))
      .mockResolvedValueOnce(makeFetchResponse(mockBlogWithPosts2))
    vi.stubGlobal('fetch', fetchMock)

    const { result } = renderHook(() => usePosts())
    await act(async () => {
      await result.current.fetchPosts(mockBlogs)
    })

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.blogMap).toEqual({
      'blog-1': 'First Blog',
      'blog-2': 'Second Blog',
    })
  })

  it('sets loading=true during fetch then false after', async () => {
    let resolveFirst!: (value: Response) => void
    const firstPromise = new Promise<Response>((resolve) => { resolveFirst = resolve })
    const fetchMock = vi.fn()
      .mockReturnValueOnce(firstPromise)
      .mockResolvedValueOnce(makeFetchResponse(mockBlogWithPosts2))
    vi.stubGlobal('fetch', fetchMock)

    const { result } = renderHook(() => usePosts())

    act(() => { void result.current.fetchPosts(mockBlogs) })
    await waitFor(() => expect(result.current.loading).toBe(true))

    await act(async () => {
      resolveFirst(makeFetchResponse(mockBlogWithPosts1))
    })
    await waitFor(() => expect(result.current.loading).toBe(false))
  })

  it('handles a failed fetch for one blog gracefully (skips it)', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(makeFetchResponse(null, false, 500))
      .mockResolvedValueOnce(makeFetchResponse(mockBlogWithPosts2))
    vi.stubGlobal('fetch', fetchMock)

    const { result } = renderHook(() => usePosts())
    await act(async () => {
      await result.current.fetchPosts(mockBlogs)
    })

    await waitFor(() => expect(result.current.loading).toBe(false))
    // Only posts from blog-2 should be present
    expect(result.current.posts).toHaveLength(1)
    expect(result.current.posts[0].id).toBe('post-3')
    expect(result.current.blogMap).toEqual({ 'blog-2': 'Second Blog' })
  })

  it('sets error on network failure', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network error')))

    const { result } = renderHook(() => usePosts())
    await act(async () => {
      await result.current.fetchPosts(mockBlogs)
    })

    await waitFor(() => expect(result.current.loading).toBe(false))
    expect(result.current.error).toBe('Network error')
  })

  it('uses bearer token in fetch headers', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(makeFetchResponse(mockBlogWithPosts1))
      .mockResolvedValueOnce(makeFetchResponse(mockBlogWithPosts2))
    vi.stubGlobal('fetch', fetchMock)

    const { result } = renderHook(() => usePosts())
    await act(async () => {
      await result.current.fetchPosts(mockBlogs)
    })

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('blog-1'),
      expect.objectContaining({ headers: { Authorization: 'Bearer test-token' } })
    )
  })
})
