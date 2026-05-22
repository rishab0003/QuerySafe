"use client"
import React, { Suspense } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import api, { API_BASE } from '../../../lib/api'

function LoginForm() {
  const router = useRouter()
  const [loading, setLoading] = React.useState(false)
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [showPassword, setShowPassword] = React.useState(false)
  const [fieldError, setFieldError] = React.useState<string | null>(null)
  const [oauth, setOauth] = React.useState({ google: false, github: false })

  React.useEffect(() => {
    api.get('/auth/oauth/providers').then((r) => setOauth(r.data)).catch(() => {})
  }, [])

  const oauthUrl = (provider: string) => {
    const base = API_BASE.replace(/\/$/, '')
    return `${base}/auth/oauth/${provider}/authorize`
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFieldError(null)
    if (!email) return setFieldError('Enter your email')
    if (!/\S+@\S+\.\S+/.test(email)) return setFieldError('Enter a valid email')
    if (!password) return setFieldError('Enter your password')
    setLoading(true)
    const id = toast.loading('Signing in...')
    try {
      const res = await api.post('/auth/login', { email, password })
      const body = res.data
      if (body.approval_pending) {
        toast.dismiss(id)
        toast(body.message || 'Awaiting admin approval', { icon: '⏳' })
        setLoading(false)
        return
      }
      toast.success('Signed in', { id })
      if (body.requires_2fa && body.temp_token) {
        try {
          localStorage.setItem('qs_temp_token', body.temp_token)
        } catch (_) {}
        setLoading(false)
        router.push('/auth/setup-2fa')
      } else if (body.access_token) {
        try {
          localStorage.setItem('qs_token', body.access_token)
        } catch (_) {}
        setLoading(false)
        router.push('/dashboard')
      }
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Sign in failed'
      toast.error(msg, { id })
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md glass p-8 rounded-lg">
        <h2 className="text-2xl font-display mb-4">Sign in to QuerySafe</h2>

        {(oauth.google || oauth.github) && (
          <div className="space-y-2 mb-4">
            {oauth.google && (
              <a
                href={oauthUrl('google')}
                className="qs-btn-secondary w-full block text-center"
              >
                Continue with Google
              </a>
            )}
            {oauth.github && (
              <a
                href={oauthUrl('github')}
                className="qs-btn-secondary w-full block text-center"
              >
                Continue with GitHub
              </a>
            )}
            <div className="text-center text-xs text-ink-400">or sign in with email</div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3" noValidate>
          <div>
            <label htmlFor="email" className="block mb-1 text-sm text-ink-400">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              className="qs-input"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
            />
          </div>
          <div>
            <label htmlFor="password" className="block mb-1 text-sm text-ink-400">
              Password
            </label>
            <div className="relative">
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                required
                className="qs-input pr-12"
                placeholder="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
              />
              <button
                type="button"
                onClick={() => setShowPassword((s) => !s)}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-sm text-ink-300"
              >
                {showPassword ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>
          {fieldError && <div className="text-sm text-red-400">{fieldError}</div>}
          <button className="qs-btn-primary w-full" disabled={loading}>
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
        <div className="mt-3 text-center text-sm">
          <a href="/auth/register" className="text-ink-300">
            Create an account
          </a>
        </div>
      </div>
    </div>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading…</div>}>
      <LoginForm />
    </Suspense>
  )
}
