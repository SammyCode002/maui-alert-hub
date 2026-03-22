/**
 * Custom hook for fetching API data with loading/error states.
 *
 * WHY a custom hook?
 * Every component that fetches data needs loading states, error handling,
 * and refresh logic. This hook handles all of that so your components
 * stay clean and focused on rendering.
 *
 * USAGE:
 *   const { data, loading, error, refresh } = useApi(getRoadClosures)
 */

import { useState, useEffect, useCallback } from 'react'

interface UseApiResult<T> {
  data: T | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  autoFetch: boolean = true
): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState<boolean>(autoFetch)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const result = await fetcher()
      setData(result)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Something went wrong'
      setError(message)
      console.error('[useApi] Fetch failed:', message)
    } finally {
      setLoading(false)
    }
  }, [fetcher])

  useEffect(() => {
    if (autoFetch) {
      refresh()
    }
  }, [autoFetch, refresh])

  return { data, loading, error, refresh }
}
