import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { useDate } from './useDate'

describe('useDate', () => {
  const { formatRelative } = useDate()

  describe('formatRelative', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('returns "just now" for less than 1 minute ago', () => {
      const now = new Date('2026-01-01T12:00:00Z')
      vi.setSystemTime(now)
      const thirtySecondsAgo = new Date('2026-01-01T11:59:30Z').toISOString()
      expect(formatRelative(thirtySecondsAgo)).toBe('just now')
    })

    it('returns "just now" for exactly 0 seconds ago', () => {
      const now = new Date('2026-01-01T12:00:00Z')
      vi.setSystemTime(now)
      expect(formatRelative(now.toISOString())).toBe('just now')
    })

    it('returns minutes ago for 1-59 minutes', () => {
      const now = new Date('2026-01-01T12:00:00Z')
      vi.setSystemTime(now)
      const fifteenMinsAgo = new Date('2026-01-01T11:45:00Z').toISOString()
      expect(formatRelative(fifteenMinsAgo)).toBe('15m ago')
    })

    it('returns "1m ago" for exactly 1 minute ago', () => {
      const now = new Date('2026-01-01T12:00:00Z')
      vi.setSystemTime(now)
      const oneMinAgo = new Date('2026-01-01T11:59:00Z').toISOString()
      expect(formatRelative(oneMinAgo)).toBe('1m ago')
    })

    it('returns "59m ago" for 59 minutes ago', () => {
      const now = new Date('2026-01-01T12:00:00Z')
      vi.setSystemTime(now)
      const fiftyNineMinsAgo = new Date('2026-01-01T11:01:00Z').toISOString()
      expect(formatRelative(fiftyNineMinsAgo)).toBe('59m ago')
    })

    it('returns hours ago for 1-23 hours', () => {
      const now = new Date('2026-01-01T12:00:00Z')
      vi.setSystemTime(now)
      const threeHoursAgo = new Date('2026-01-01T09:00:00Z').toISOString()
      expect(formatRelative(threeHoursAgo)).toBe('3h ago')
    })

    it('returns "1h ago" for exactly 1 hour ago', () => {
      const now = new Date('2026-01-01T12:00:00Z')
      vi.setSystemTime(now)
      const oneHourAgo = new Date('2026-01-01T11:00:00Z').toISOString()
      expect(formatRelative(oneHourAgo)).toBe('1h ago')
    })

    it('returns "23h ago" for 23 hours ago', () => {
      const now = new Date('2026-01-01T12:00:00Z')
      vi.setSystemTime(now)
      const twentyThreeHoursAgo = new Date('2025-12-31T13:00:00Z').toISOString()
      expect(formatRelative(twentyThreeHoursAgo)).toBe('23h ago')
    })

    it('returns days ago for 1+ days', () => {
      const now = new Date('2026-01-01T12:00:00Z')
      vi.setSystemTime(now)
      const twoDaysAgo = new Date('2025-12-30T12:00:00Z').toISOString()
      expect(formatRelative(twoDaysAgo)).toBe('2d ago')
    })

    it('returns "1d ago" for exactly 24 hours ago', () => {
      const now = new Date('2026-01-01T12:00:00Z')
      vi.setSystemTime(now)
      const oneDayAgo = new Date('2025-12-31T12:00:00Z').toISOString()
      expect(formatRelative(oneDayAgo)).toBe('1d ago')
    })

    it('returns "7d ago" for a week ago', () => {
      const now = new Date('2026-01-08T12:00:00Z')
      vi.setSystemTime(now)
      const oneWeekAgo = new Date('2026-01-01T12:00:00Z').toISOString()
      expect(formatRelative(oneWeekAgo)).toBe('7d ago')
    })
  })
})
