/**
 * Persists a checklist state to localStorage.
 * Uses item text as key so state survives list reordering.
 */

import { useState, useEffect } from 'react'

const STORAGE_KEY = 'maui-prep-checklist'

export function useChecklist(items: string[]) {
  const [checked, setChecked] = useState<Record<string, boolean>>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      return stored ? JSON.parse(stored) : {}
    } catch {
      return {}
    }
  })

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(checked))
  }, [checked])

  const toggle = (item: string) => {
    setChecked(prev => ({ ...prev, [item]: !prev[item] }))
  }

  const reset = () => {
    setChecked({})
    localStorage.removeItem(STORAGE_KEY)
  }

  const checkedCount = items.filter(item => checked[item]).length

  return { checked, toggle, reset, checkedCount }
}
