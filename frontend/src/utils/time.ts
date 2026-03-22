/**
 * Time formatting utilities.
 */

/**
 * Returns a human-readable relative time string from an ISO datetime string.
 * e.g. "Just now", "3m ago", "2h ago", "1d ago"
 */
/**
 * Returns true when data is older than thresholdMinutes (default 15).
 * Used to show stale data warnings.
 */
export function isStale(isoString: string | null | undefined, thresholdMinutes = 15): boolean {
  if (!isoString) return false
  const ms = Date.now() - new Date(isoString).getTime()
  return ms > thresholdMinutes * 60 * 1000
}

export function timeAgo(isoString: string | null | undefined): string | null {
  if (!isoString) return null
  const date = new Date(isoString)
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000)
  if (seconds < 60) return 'Just now'
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}
