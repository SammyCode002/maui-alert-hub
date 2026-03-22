/**
 * Simple loading and error state components.
 */

import { Loader2, AlertCircle } from 'lucide-react'

export function LoadingSpinner({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <Loader2 className="w-8 h-8 text-ocean-400 animate-spin" />
      <p className="text-ocean-400 text-sm">{message}</p>
    </div>
  )
}

export function ErrorMessage({
  message = 'Something went wrong',
  onRetry,
}: {
  message?: string
  onRetry?: () => void
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3">
      <AlertCircle className="w-8 h-8 text-red-400" />
      <p className="text-red-300 text-sm text-center">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 px-4 py-2 text-sm font-medium rounded-lg bg-ocean-700 hover:bg-ocean-600 transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  )
}

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-8 gap-2">
      <p className="text-ocean-400 text-sm text-center">{message}</p>
    </div>
  )
}
