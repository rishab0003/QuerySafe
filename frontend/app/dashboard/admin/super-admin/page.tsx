"use client"
import React, { useState } from 'react'
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

  // Load profile only once on mount. Dependence on `user` caused an infinite loop because setting the user updates the store and re‑triggers this effect.
  React.useEffect(() => {
    const token = localStorage.getItem('qs_token')
    if (!token) {
      router.replace('/auth/login')
      return
    }
    // If already have a user but not admin, redirect immediately.
    if (user && user.role !== 'admin') {
      router.replace('/dashboard')
      return
    }
    loadProfile()
    // Empty dependency array ensures this runs only once.
  }, [])

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
      toast.success('User account created and pre-approved')
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
    return (
      <div className="flex items-center gap-2 p-8 text-xs text-[--text-muted]">
        <span className="loading-dot"></span>
        <span className="loading-dot"></span>
        <span className="loading-dot"></span>
        Authenticating Super Admin...
      </div>
    )
  }

  return (
    <div className="p-6 md:p-8 space-y-6 max-w-5xl w-full mx-auto overflow-y-auto scrollbar-thin">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--border-subtle)] pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-[--text-primary]">Super Admin Portal</h1>
          <p className="text-xs text-[--text-muted] mt-0.5">
            Directly provision approved employee credentials, bypass registration verification, and manage workspace permissions.
          </p>
        </div>
        <Link href="/dashboard/admin" className="text-xs text-[var(--accent-cyan)] hover:underline border border-[var(--accent-cyan)]/20 px-3 py-1.5 rounded-lg bg-[var(--accent-cyan)]/5 font-medium transition-all">
          ← Back to Approvals
        </Link>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        {/* Form panel */}
        <form onSubmit={handleSubmit} className="glass p-6 rounded-2xl border border-white/5 shadow-card space-y-4">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[--text-secondary] border-b border-white/5 pb-2">
            Provision New Employee Credentials
          </h3>

          <div>
            <label className="block text-[10px] font-semibold text-[--text-muted] uppercase mb-1">Corporate Email Address</label>
            <input
              type="email"
              required
              className="qs-input w-full"
              value={form.email}
              onChange={(e) => setForm((curr) => ({ ...curr, email: e.target.value }))}
              placeholder="e.g. employee@company.com"
            />
          </div>

          <div>
            <label className="block text-[10px] font-semibold text-[--text-muted] uppercase mb-1">Temporary Password</label>
            <input
              type="text"
              required
              className="qs-input w-full font-mono text-xs"
              value={form.password}
              onChange={(e) => setForm((curr) => ({ ...curr, password: e.target.value }))}
              placeholder="Min. 8 characters"
            />
          </div>

          <div>
            <label className="block text-[10px] font-semibold text-[--text-muted] uppercase mb-1">Full Legal Name</label>
            <input
              type="text"
              required
              className="qs-input w-full"
              value={form.full_name}
              onChange={(e) => setForm((curr) => ({ ...curr, full_name: e.target.value }))}
              placeholder="e.g. Jane Doe"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="block text-[10px] font-semibold text-[--text-muted] uppercase mb-1">Department</label>
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
              <label className="block text-[10px] font-semibold text-[--text-muted] uppercase mb-1">Assigned Role</label>
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

          <button
            type="submit"
            disabled={submitting}
            className="qs-btn-primary w-full py-3 mt-2 flex items-center justify-center font-semibold text-xs shadow-glow cursor-pointer"
          >
            {submitting ? 'Provisioning...' : 'Provision and Approve Account'}
          </button>
        </form>

        {/* Info & Created view */}
        <div className="space-y-6">
          <div className="glass p-5 rounded-2xl border border-white/5 shadow-card space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[--text-muted] border-b border-white/5 pb-1">
              Workspace Administration
            </h4>
            <p className="text-xs text-[--text-muted] leading-relaxed">
              Provisioning instantly injects pre-approved rows into the authentication store. Passwords are encrypted on-the-fly, enabling employees to sign in directly.
            </p>
          </div>

          {createdUser && (
            <div className="glass-elevated p-5 rounded-2xl border border-[var(--accent-cyan)]/30 shadow-glow space-y-2.5 animate-fade-in">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-[var(--accent-cyan)]">Account Created</h4>
              <div className="space-y-1 text-xs font-mono bg-black/20 p-3 rounded-xl border border-white/5">
                <div><span className="text-[--text-muted]">EMAIL:</span> {createdUser.email}</div>
                <div><span className="text-[--text-muted]">NAME:</span> {createdUser.full_name}</div>
                <div><span className="text-[--text-muted]">ROLE:</span> {createdUser.role}</div>
                <div><span className="text-[--text-muted]">DEPT:</span> {createdUser.department}</div>
                <div><span className="text-[--text-muted]">STATUS:</span> {createdUser.approval_status}</div>
              </div>
            </div>
          )}

          {/* User Management List */}
          <div className="glass p-5 rounded-2xl border border-white/5 shadow-card space-y-4">
            <div className="flex items-center justify-between gap-3">
              <div>
                <h4 className="text-xs font-semibold uppercase tracking-wider text-[--text-secondary]">User Register</h4>
                <p className="text-[10px] text-[--text-muted] mt-0.5">Active profiles inside PostgreSQL database.</p>
              </div>
              <button
                type="button"
                className="text-[10px] font-semibold text-[var(--accent-cyan)] border border-[var(--accent-cyan)]/20 px-2 py-1 rounded bg-[var(--accent-cyan)]/5 hover:bg-[var(--accent-cyan)]/15 transition-all cursor-pointer"
                onClick={loadUsers}
                disabled={refreshing}
              >
                {refreshing ? 'Reloading...' : 'Refresh List'}
              </button>
            </div>

            <div className="overflow-x-auto rounded-xl border border-white/5 scrollbar-thin">
              <table className="min-w-full text-xs text-left font-mono">
                <thead className="bg-white/5 text-[--text-muted]">
                  <tr>
                    <th className="px-3 py-2.5 text-left font-semibold">Email</th>
                    <th className="px-3 py-2.5 text-left font-semibold">Name</th>
                    <th className="px-3 py-2.5 text-left font-semibold">Role</th>
                    <th className="px-3 py-2.5 text-left font-semibold">Dept</th>
                    <th className="px-3 py-2.5 text-left font-semibold">Status</th>
                    <th className="px-3 py-2.5 text-left font-semibold">2FA</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {users.length === 0 ? (
                    <tr>
                      <td className="px-3 py-4 text-[--text-muted] text-center" colSpan={6}>
                        No records loaded.
                      </td>
                    </tr>
                  ) : (
                    users.map((entry) => (
                      <tr key={entry.id} className="hover:bg-white/[0.02] transition-colors">
                        <td className="px-3 py-2.5 text-white max-w-[120px] truncate" title={entry.email}>
                          {entry.email}
                        </td>
                        <td className="px-3 py-2.5 text-white/80 max-w-[100px] truncate">{entry.full_name}</td>
                        <td className="px-3 py-2.5 text-[var(--accent-cyan)]">{entry.role}</td>
                        <td className="px-3 py-2.5 text-white/70 capitalize">{entry.department}</td>
                        <td className="px-3 py-2.5">
                          <span className={`text-[9px] px-1.5 py-0.5 rounded-full ${
                            entry.approval_status === 'approved' ? 'bg-[var(--accent-green)]/15 text-[var(--accent-green)]' :
                            'bg-[var(--accent-cyan)]/15 text-[var(--accent-cyan)]'
                          }`}>
                            {entry.approval_status}
                          </span>
                        </td>
                        <td className="px-3 py-2.5 text-[--text-muted]">
                          {entry.is_2fa_enabled ? 'Active' : 'Off'}
                        </td>
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
  )
}
