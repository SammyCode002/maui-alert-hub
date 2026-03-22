/**
 * Admin panel — accessible at /#admin
 *
 * Lets authorized users post community alerts (power outages,
 * water main breaks, etc.) that appear on the main dashboard.
 *
 * Auth: enter the ADMIN_TOKEN (set in Render env vars).
 * Token is stored in sessionStorage so it persists while the tab is open.
 */

import { useState, useEffect } from 'react'
import { ShieldCheck, Plus, Trash2, LogOut, AlertTriangle } from 'lucide-react'
import { adminGetAlerts, adminCreateAlert, adminDeleteAlert } from '../utils/api'
import type { CommunityAlert } from '../utils/types'
import { timeAgo } from '../utils/time'

const SESSION_TOKEN_KEY = 'admin-token'

export default function AdminPage() {
  const [token, setToken] = useState(() => sessionStorage.getItem(SESSION_TOKEN_KEY) ?? '')
  const [authed, setAuthed] = useState(false)
  const [alerts, setAlerts] = useState<CommunityAlert[]>([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  // Form state
  const [title, setTitle] = useState('')
  const [message, setMessage] = useState('')
  const [severity, setSeverity] = useState<'info' | 'warning' | 'danger'>('warning')
  const [expiresAt, setExpiresAt] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const login = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await adminGetAlerts(token)
      setAlerts(data.alerts)
      setAuthed(true)
      sessionStorage.setItem(SESSION_TOKEN_KEY, token)
    } catch {
      setError('Invalid token. Check your ADMIN_TOKEN env var.')
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    setAuthed(false)
    setToken('')
    sessionStorage.removeItem(SESSION_TOKEN_KEY)
  }

  const refreshAlerts = async () => {
    const data = await adminGetAlerts(token)
    setAlerts(data.alerts)
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      await adminCreateAlert(token, {
        title,
        message,
        severity,
        expires_at: expiresAt || null,
      })
      setTitle('')
      setMessage('')
      setSeverity('warning')
      setExpiresAt('')
      await refreshAlerts()
    } catch (err) {
      setError(String(err))
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id: number) => {
    await adminDeleteAlert(token, id)
    await refreshAlerts()
  }

  // Try auto-login if token already in sessionStorage
  useEffect(() => {
    if (token) login()
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  if (!authed) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4">
        <div className="card w-full max-w-sm space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <ShieldCheck className="w-5 h-5 text-ocean-400" />
            <h1 className="font-display font-bold text-lg">Admin Panel</h1>
          </div>
          <input
            type="password"
            placeholder="Admin token"
            value={token}
            onChange={e => setToken(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && login()}
            className="w-full bg-white/[0.06] border border-white/[0.09] rounded-xl px-4 py-2.5 text-white text-sm placeholder-ocean-600 focus:outline-none focus:border-ocean-500"
          />
          {error && <p className="text-red-400 text-xs">{error}</p>}
          <button
            onClick={login}
            disabled={loading || !token}
            className="w-full bg-ocean-500 hover:bg-ocean-400 text-white font-semibold py-2.5 rounded-xl transition-colors disabled:opacity-50"
          >
            {loading ? 'Checking...' : 'Sign in'}
          </button>
          <a href="/" className="block text-center text-ocean-500 text-xs hover:text-ocean-300 transition-colors">
            ← Back to dashboard
          </a>
        </div>
      </div>
    )
  }

  const severityColors: Record<string, string> = {
    info: 'text-blue-400',
    warning: 'text-amber-400',
    danger: 'text-red-400',
  }

  return (
    <div className="min-h-screen">
      <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-ocean-400" />
            <h1 className="font-display font-bold text-xl">Admin Panel</h1>
          </div>
          <div className="flex items-center gap-2">
            <a href="/" className="text-ocean-500 text-sm hover:text-ocean-300 transition-colors">Dashboard</a>
            <button onClick={logout} className="p-2 rounded-xl bg-white/[0.05] border border-white/[0.09] hover:bg-white/[0.10] transition-colors">
              <LogOut className="w-4 h-4 text-ocean-400" />
            </button>
          </div>
        </div>

        {/* Create alert form */}
        <div className="card space-y-3">
          <h2 className="font-display font-semibold text-sm text-ocean-300 uppercase tracking-wide">
            Post Community Alert
          </h2>
          <form onSubmit={handleCreate} className="space-y-3">
            <input
              type="text"
              placeholder="Title (e.g. Power outage in Kihei)"
              value={title}
              onChange={e => setTitle(e.target.value)}
              required
              maxLength={120}
              className="w-full bg-white/[0.06] border border-white/[0.09] rounded-xl px-4 py-2.5 text-white text-sm placeholder-ocean-600 focus:outline-none focus:border-ocean-500"
            />
            <textarea
              placeholder="Details..."
              value={message}
              onChange={e => setMessage(e.target.value)}
              required
              rows={3}
              maxLength={1000}
              className="w-full bg-white/[0.06] border border-white/[0.09] rounded-xl px-4 py-2.5 text-white text-sm placeholder-ocean-600 focus:outline-none focus:border-ocean-500 resize-none"
            />
            <div className="flex gap-3">
              <select
                value={severity}
                onChange={e => setSeverity(e.target.value as typeof severity)}
                className="bg-white/[0.06] border border-white/[0.09] rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none focus:border-ocean-500"
              >
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="danger">Danger</option>
              </select>
              <input
                type="datetime-local"
                value={expiresAt}
                onChange={e => setExpiresAt(e.target.value)}
                placeholder="Expires (optional)"
                className="flex-1 bg-white/[0.06] border border-white/[0.09] rounded-xl px-3 py-2.5 text-white text-sm focus:outline-none focus:border-ocean-500"
              />
            </div>
            {error && <p className="text-red-400 text-xs">{error}</p>}
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center gap-2 bg-ocean-500 hover:bg-ocean-400 text-white font-semibold px-4 py-2.5 rounded-xl transition-colors disabled:opacity-50"
            >
              <Plus className="w-4 h-4" />
              {submitting ? 'Posting...' : 'Post alert'}
            </button>
          </form>
        </div>

        {/* Alert list */}
        <div className="space-y-3">
          <h2 className="font-display font-semibold text-sm text-ocean-300 uppercase tracking-wide">
            All alerts ({alerts.length})
          </h2>
          {alerts.length === 0 && (
            <p className="text-ocean-600 text-sm">No alerts posted yet.</p>
          )}
          {alerts.map(alert => (
            <div key={alert.id} className={`card flex items-start gap-3 ${!alert.is_active ? 'opacity-40' : ''}`}>
              <AlertTriangle className={`w-4 h-4 mt-0.5 flex-shrink-0 ${severityColors[alert.severity]}`} />
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-medium">{alert.title}</p>
                <p className="text-ocean-400 text-xs mt-0.5">{alert.message}</p>
                <p className="text-ocean-600 text-xs mt-1">
                  {timeAgo(alert.created_at)} · {alert.is_active ? 'Active' : 'Inactive'}
                  {alert.expires_at && ` · expires ${timeAgo(alert.expires_at)}`}
                </p>
              </div>
              {alert.is_active && (
                <button
                  onClick={() => handleDelete(alert.id)}
                  className="flex-shrink-0 p-1.5 text-ocean-600 hover:text-red-400 transition-colors"
                  title="Deactivate"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
