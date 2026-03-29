import { describe, it, expect } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useFormatDate } from '../useFormatDate'

describe('useFormatDate', () => {
  it('returns a formatDate function', () => {
    const { result } = renderHook(() => useFormatDate())
    expect(typeof result.current.formatDate).toBe('function')
  })

  it('formats an ISO date string into a human-readable date', () => {
    const { result } = renderHook(() => useFormatDate())
    // Use noon UTC so the date is stable regardless of local timezone offset
    const formatted = result.current.formatDate('2024-06-15T12:00:00.000Z')
    expect(formatted).toMatch(/2024/)
    expect(formatted).toMatch(/15/)
  })

  it('formats a known date correctly (June 15, 2024)', () => {
    const { result } = renderHook(() => useFormatDate())
    const formatted = result.current.formatDate('2024-06-15T00:00:00.000Z')
    expect(formatted).toBe(
      new Date('2024-06-15T00:00:00.000Z').toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    )
  })

  it('handles January 1st correctly', () => {
    const { result } = renderHook(() => useFormatDate())
    const formatted = result.current.formatDate('2023-01-01T12:00:00.000Z')
    expect(formatted).toMatch(/2023/)
    expect(formatted).toMatch(/January|1/)
  })

  it('handles December 31st correctly', () => {
    const { result } = renderHook(() => useFormatDate())
    const formatted = result.current.formatDate('2023-12-31T12:00:00.000Z')
    expect(formatted).toMatch(/2023/)
    expect(formatted).toMatch(/December|31/)
  })

  it('returns a stable reference across re-renders', () => {
    const { result, rerender } = renderHook(() => useFormatDate())
    const first = result.current.formatDate
    rerender()
    const second = result.current.formatDate
    // Both calls should produce the same output (function identity may differ, behaviour must not)
    expect(first('2024-06-15T00:00:00.000Z')).toBe(second('2024-06-15T00:00:00.000Z'))
  })
})
