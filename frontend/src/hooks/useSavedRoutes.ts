/**
 * Persists a set of saved road IDs to localStorage.
 * Used to let users bookmark roads they care about.
 */

import { useState, useEffect } from 'react'

const STORAGE_KEY = 'maui-saved-routes'

export function useSavedRoutes() {
  const [saved, setSaved] = useState<Set<string>>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? new Set(JSON.parse(stored)) : new Set()
    } catch {
      return new Set()
    }
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...saved]))
  }, [saved])

  const toggle = (id: string) => {
    setSaved(prev => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const isSaved = (id: string) => saved.has(id)

  return { saved, toggle, isSaved }
}
