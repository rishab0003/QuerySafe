"use client"
import React from 'react'
import { useRouter } from 'next/navigation'
import api, { API_BASE } from '../../../lib/api'
import toast from 'react-hot-toast'

const DEPARTMENTS = ['general', 'engineering', 'hr', 'finance', 'sales', 'support']

export default function RegisterPage() {
  const router = useRouter()
  const [fullName, setFullName] = React.useState('')
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [department, setDepartment] = React.useState('general')
  const [loading, setLoading] = React.useState(false)
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

  function validatePassword(p: string) {
    if (p.length < 8) return 'Password must be at least 8 characters'
    if (!/[a-z]/.test(p)) return 'Password must include a lowercase letter'
    if (!/[A-Z]/.test(p)) return 'Password must include an uppercase letter'
    if (!/[0-9]/.test(p)) return 'Password must include a number'
    if (!/[^A-Za-z0-9]/.test(p)) return 'Password must include a symbol'
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFieldError(null)
    if (!fullName.trim()) return setFieldError('Enter your full name')
    if (!email) return setFieldError('Enter your email')
    if (!/\S+@\S+\.\S+/.test(email)) return setFieldError('Enter a valid email')
    const pwErr = validatePassword(password)
    if (pwErr) return setFieldError(pwErr)

    setLoading(true)
    const id = toast.loading('Creating account...')
    try {
      await api.post('/auth/register', {
        full_name: fullName.trim(),
        email,
        password,
        department,
      })
      toast.dismiss(id)
      toast.success('Account created. An admin must approve you before you can sign in.', {
        duration: 6000,
      })
      router.push('/auth/login')
    } catch (err: any) {
      toast.dismiss(id)
      const msg = err?.response?.data?.detail || err?.message || 'Registration failed'
      toast.error(typeof msg === 'string' ? msg : JSON.stringify(msg))
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md glass p-8 rounded-lg">
        <h2 className="text-2xl font-display mb-2">Create account</h2>
        <p className="text-sm text-ink-400 mb-4">
          Your admin will assign your role after approval.
        </p>

        {(oauth.google || oauth.github) && (
          <div className="space-y-2 mb-4">
            {oauth.google && (
              <a href={oauthUrl('google')} className="qs-btn-secondary w-full block text-center">
                Sign up with Google
              </a>
            )}
            {oauth.github && (
              <a href={oauthUrl('github')} className="qs-btn-secondary w-full block text-center">
                Sign up with GitHub
              </a>
            )}
            <div className="text-center text-xs text-ink-400">or register with email</div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-3" noValidate>
          <div>
            <label htmlFor="name" className="block mb-1 text-sm text-ink-400">
              Full name
            </label>
            <input
              id="name"
              name="name"
              className="qs-input"
              placeholder="Your name"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              disabled={loading}
            />
          </div>
          <div>
            <label htmlFor="email" className="block mb-1 text-sm text-ink-400">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              className="qs-input"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
            />
          </div>
          <div>
            <label htmlFor="department" className="block mb-1 text-sm text-ink-400">
              Department
            </label>
            <select
              id="department"
              className="qs-input"
              value={department}
              onChange={(e) => setDepartment(e.target.value)}
              disabled={loading}
            >
              {DEPARTMENTS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
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
                autoComplete="new-password"
                className="qs-input pr-12"
                placeholder="Create a strong password"
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
            {loading ? 'Creating…' : 'Create account'}
          </button>
        </form>
        <div className="mt-3 text-center text-sm">
          <a href="/auth/login" className="text-ink-300">
            Already have an account? Sign in
          </a>
        </div>
      </div>
    </div>
  )
}
