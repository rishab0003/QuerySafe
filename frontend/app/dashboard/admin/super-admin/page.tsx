"use client"
import React from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import api from '../../../../lib/api'
import useAuthStore from '../../../../lib/store'

type CreatedUser = {
  id: string
  email: string
  full_name: string
  department: string
  role: string
  approval_status: string
}

type UserRow = CreatedUser & {
  is_active: boolean
  is_2fa_enabled: boolean
  created_at: string
}

const ROLES = ['viewer', 'hr', 'finance', 'sales', 'support', 'admin']
const DEPARTMENTS = ['general', 'engineering', 'hr', 'finance', 'sales', 'support']

export default function SuperAdminPage() {
  const router = useRouter()
  const user = useAuthStore((s) => s.user)
  const [loading, setLoading] = React.useState(true)
  const [submitting, setSubmitting] = React.useState(false)
  const [refreshing, setRefreshing] = React.useState(false)
  const [createdUser, setCreatedUser] = React.useState<CreatedUser | null>(null)
  const [users, setUsers] = React.useState<UserRow[]>([])
  const [form, setForm] = React.useState({
    email: '',
    password: '',
    full_name: '',
    department: 'general',
    role: 'viewer',
  })

  React.useEffect(() => {
    const token = localStorage.getItem('qs_token')
    if (!token) {
      router.replace('/auth/login')
      return
    }
    if (user && user.role !== 'admin') {
      router.replace('/dashboard')
      return
    }
    loadProfile()
  }, [router, user])

  async function loadProfile() {
    try {
      const me = await api.get('/auth/me')
      useAuthStore.getState().setUser(me.data)
      if (me.data.role !== 'admin') {
        router.replace('/dashboard')
        return
      }
      await loadUsers()
    } catch {
      router.replace('/auth/login')
      return
    } finally {
      setLoading(false)
    }
  }

  async function loadUsers() {
    setRefreshing(true)
    try {
      const res = await api.get('/admin/users')
      setUsers(res.data)
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to load employees')
    } finally {
      setRefreshing(false)
    }
  }

  async function handleSubmit(ev: React.FormEvent) {
    ev.preventDefault()
    setSubmitting(true)
    setCreatedUser(null)
    try {
      const res = await api.post('/admin/users', form)
      setCreatedUser(res.data)
      toast.success('User account created')
      await loadUsers()
      setForm({
        email: '',
        password: '',
        full_name: '',
        department: 'general',
        role: 'viewer',
      })
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to create account')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return <div className="min-h-screen bg-[--bg-void] text-[--text-primary] p-8">Loading…</div>
  }

  return (
    <div className="min-h-screen bg-[--bg-void] text-[--text-primary] p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-3xl font-display">Super Admin</h1>
            <p className="text-sm text-[--text-muted] mt-1">
              Provision approved user accounts with login ids, passwords, roles, and departments.
            </p>
          </div>
          <Link href="/dashboard/admin" className="text-sm text-[--accent-cyan] hover:underline">
            ← Back to approvals
          </Link>
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <form onSubmit={handleSubmit} className="glass p-6 rounded-2xl space-y-4">
            <div>
              <label className="block text-sm text-[--text-muted] mb-1">Login id / email</label>
              <input
                type="email"
                required
                className="qs-input w-full"
                value={form.email}
                onChange={(e) => setForm((curr) => ({ ...curr, email: e.target.value }))}
                placeholder="name@company.com"
              />
            </div>

            <div>
              <label className="block text-sm text-[--text-muted] mb-1">Temporary password</label>
              <input
                type="text"
                required
                className="qs-input w-full"
                value={form.password}
                onChange={(e) => setForm((curr) => ({ ...curr, password: e.target.value }))}
                placeholder="At least 8 characters"
              />
            </div>

            <div>
              <label className="block text-sm text-[--text-muted] mb-1">Full name</label>
              <input
                type="text"
                required
                className="qs-input w-full"
                value={form.full_name}
                onChange={(e) => setForm((curr) => ({ ...curr, full_name: e.target.value }))}
                placeholder="Person name"
              />
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <label className="block text-sm text-[--text-muted] mb-1">Department</label>
                <select
                  className="qs-select w-full"
                  value={form.department}
                  onChange={(e) => setForm((curr) => ({ ...curr, department: e.target.value }))}
                >
                  {DEPARTMENTS.map((department) => (
                    <option key={department} value={department}>
                      {department}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm text-[--text-muted] mb-1">Role</label>
                <select
                  className="qs-select w-full"
                  value={form.role}
                  onChange={(e) => setForm((curr) => ({ ...curr, role: e.target.value }))}
                >
                  {ROLES.map((role) => (
                    <option key={role} value={role}>
                      {role}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <button type="submit" className="qs-btn-primary w-full sm:w-auto" disabled={submitting}>
              {submitting ? 'Creating account…' : 'Create user'}
            </button>
          </form>

          <div className="space-y-4">
            <div className="glass p-6 rounded-2xl">
              <div className="text-sm uppercase tracking-[0.2em] text-[--text-muted] mb-2">What this does</div>
              <p className="text-sm text-[--text-secondary] leading-6">
                This page creates an approved account immediately, so the person can sign in without waiting for a manual approval step.
              </p>
              <p className="text-sm text-[--text-secondary] leading-6 mt-3">
                PostgreSQL should remain the storage layer for these credentials because the existing auth system already uses it, keeps passwords hashed centrally, and fits the approval workflow you already have.
              </p>
            </div>

            {createdUser && (
              <div className="glass-elevated p-6 rounded-2xl border border-[var(--accent-cyan)]/30">
                <div className="text-sm uppercase tracking-[0.2em] text-[--text-muted] mb-2">Created</div>
                <div className="space-y-1 text-sm">
                  <div><span className="text-[--text-muted]">Email:</span> {createdUser.email}</div>
                  <div><span className="text-[--text-muted]">Name:</span> {createdUser.full_name}</div>
                  <div><span className="text-[--text-muted]">Role:</span> {createdUser.role}</div>
                  <div><span className="text-[--text-muted]">Department:</span> {createdUser.department}</div>
                  <div><span className="text-[--text-muted]">Status:</span> {createdUser.approval_status}</div>
                </div>
              </div>
            )}

            <div className="glass p-6 rounded-2xl">
              <div className="flex items-center justify-between gap-3 mb-4">
                <div>
                  <div className="text-sm uppercase tracking-[0.2em] text-[--text-muted]">Employees</div>
                  <p className="text-sm text-[--text-secondary] mt-1">Approved and pending user records from the auth store.</p>
                </div>
                <button
                  type="button"
                  className="qs-btn-ghost text-sm"
                  onClick={loadUsers}
                  disabled={refreshing}
                >
                  {refreshing ? 'Refreshing…' : 'Refresh'}
                </button>
              </div>

              <div className="overflow-x-auto rounded-xl border border-[var(--border-subtle)]">
                <table className="min-w-full text-sm">
                  <thead className="bg-[var(--bg-surface)] text-[--text-muted]">
                    <tr>
                      <th className="px-4 py-3 text-left font-medium">Email</th>
                      <th className="px-4 py-3 text-left font-medium">Name</th>
                      <th className="px-4 py-3 text-left font-medium">Role</th>
                      <th className="px-4 py-3 text-left font-medium">Department</th>
                      <th className="px-4 py-3 text-left font-medium">Status</th>
                      <th className="px-4 py-3 text-left font-medium">2FA</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.length === 0 ? (
                      <tr>
                        <td className="px-4 py-4 text-[--text-muted]" colSpan={6}>
                          No employee records found.
                        </td>
                      </tr>
                    ) : (
                      users.map((entry) => (
                        <tr key={entry.id} className="border-t border-[var(--border-subtle)]">
                          <td className="px-4 py-3">{entry.email}</td>
                          <td className="px-4 py-3">{entry.full_name}</td>
                          <td className="px-4 py-3 capitalize">{entry.role}</td>
                          <td className="px-4 py-3 capitalize">{entry.department}</td>
                          <td className="px-4 py-3 capitalize">{entry.approval_status}</td>
                          <td className="px-4 py-3">{entry.is_2fa_enabled ? 'Enabled' : 'Disabled'}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
