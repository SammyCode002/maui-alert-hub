/**
 * PWA install prompt hook.
 *
 * Handles two install paths:
 *   Android/Chrome/Edge: intercepts `beforeinstallprompt`, lets us trigger it from a button
 *   iOS Safari:          no event exists — we detect the platform and show manual instructions
 *
 * Persists dismissal to localStorage so the banner stays gone after the user closes it.
 */

import { useState, useEffect } from 'react'

// TypeScript doesn't include BeforeInstallPromptEvent in its DOM lib yet
interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

const DISMISSED_KEY = 'install-banner-dismissed'

function isRunningStandalone(): boolean {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    // Safari-specific standalone flag
    (window.navigator as unknown as { standalone?: boolean }).standalone === true
  )
}

function isIOS(): boolean {
  return /iphone|ipad|ipod/i.test(navigator.userAgent)
}

function isIOSSafari(): boolean {
  // Must be iOS AND Safari AND NOT Chrome/Firefox on iOS (which can't install PWAs)
  return (
    isIOS() &&
    /safari/i.test(navigator.userAgent) &&
    !/crios|fxios|opios/i.test(navigator.userAgent)
  )
}

export function useInstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null)
  const [installed, setInstalled] = useState(false)
  const [dismissed, setDismissed] = useState(
    () => localStorage.getItem(DISMISSED_KEY) === 'true'
  )

  useEffect(() => {
    if (isRunningStandalone()) {
      setInstalled(true)
      return
    }

    const handler = (e: Event) => {
      e.preventDefault()
      setDeferredPrompt(e as BeforeInstallPromptEvent)
    }
    window.addEventListener('beforeinstallprompt', handler)

    // If user installs via the browser's own UI, hide our banner
    window.addEventListener('appinstalled', () => setInstalled(true))

    return () => window.removeEventListener('beforeinstallprompt', handler)
  }, [])

  const install = async () => {
    if (!deferredPrompt) return
    await deferredPrompt.prompt()
    const { outcome } = await deferredPrompt.userChoice
    if (outcome === 'accepted') setInstalled(true)
    setDeferredPrompt(null)
  }

  const dismiss = () => {
    setDismissed(true)
    localStorage.setItem(DISMISSED_KEY, 'true')
  }

  // Show the banner when:
  // - not already installed / running standalone
  // - not dismissed
  // - either: Android (has deferred prompt) OR iOS Safari (manual instructions)
  const showBanner =
    !installed &&
    !dismissed &&
    (deferredPrompt !== null || isIOSSafari())

  return {
    showBanner,
    isIOS: isIOS(),
    install,
    dismiss,
  }
}
