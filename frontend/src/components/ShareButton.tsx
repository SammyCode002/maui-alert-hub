/**
 * Share button using the Web Share API.
 * Renders nothing on browsers that don't support navigator.share (desktops).
 */

import { useState } from 'react'
import { Share2, Check } from 'lucide-react'

interface ShareButtonProps {
  title: string
  text: string
}

export default function ShareButton({ title, text }: ShareButtonProps) {
  const [shared, setShared] = useState(false)

  if (!('share' in navigator)) return null

  const handleShare = async (e: React.MouseEvent) => {
    e.stopPropagation()
    try {
      await navigator.share({ title, text, url: window.location.href })
      setShared(true)
      setTimeout(() => setShared(false), 2000)
    } catch {
      // User cancelled or browser blocked — no-op
    }
  }

  return (
    <button
      onClick={handleShare}
      className="text-ocean-600 hover:text-ocean-300 transition-colors"
      aria-label="Share"
    >
      {shared
        ? <Check className="w-4 h-4 text-green-400" />
        : <Share2 className="w-4 h-4" />
      }
    </button>
  )
}
