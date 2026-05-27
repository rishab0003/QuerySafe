"use client"
import React from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import api from '../../../lib/api'
import useAuthStore from '../../../lib/store'

type Employee = {
  id: string
  email: string
  full_name: string
  department: string
  role: string
  approval_status: string
  is_active: boolean
}

const ROLES = ['viewer', 'hr', 'finance', 'sales', 'support', 'admin']
const DEPARTMENTS = ['general', 'engineering', 'hr', 'finance', 'sales', 'support']

export default function AdminPage() {
  const router = useRouter()
  const user = useAuthStore((s) => s.user)
  const [employees, setEmployees] = React.useState<Employee[]>([])
  const [filter, setFilter] = React.useState<'pending' | ''>('pending')
  const [loading, setLoading] = React.useState(true)
  const [roleById, setRoleById] = React.useState<Record<string, string>>({})
  const [deptById, setDeptById] = React.useState<Record<string, string>>({})

  React.useEffect(() => {
    const token = localStorage.getItem('qs_token')
    if (!token) {
      router.replace('/auth/login')
      return
    }
    if (user) {
      if (user.role !== 'admin') {
        router.replace('/dashboard')
      } else {
        loadEmployees()
      }
    } else {
      loadProfile()
    }
  }, [])

  async function loadProfile() {
    try {
      const me = await api.get('/auth/me')
      useAuthStore.getState().setUser(me.data)
      if (me.data.role !== 'admin') {
        router.replace('/dashboard')
        return
      }
      await loadEmployees()
    } catch {
      router.replace('/auth/login')
    }
  }

  async function loadEmployees() {
    setLoading(true)
    try {
      // Fetch all users without server-side filtering to have correct tab counts
      const res = await api.get('/admin/users')
      setEmployees(res.data)
      const roles: Record<string, string> = {}
      const depts: Record<string, string> = {}
      for (const e of res.data) {
        roles[e.id] = e.role === 'viewer' ? 'hr' : e.role
        depts[e.id] = e.department || 'general'
      }
      setRoleById(roles)
      setDeptById(depts)
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to load employees')
    } finally {
      setLoading(false)
    }
  }

  async function approve(id: string) {
    try {
      await api.post(`/admin/users/${id}/approve`, {
        role: roleById[id] || 'viewer',
        department: deptById[id] || 'general',
      })
      toast.success('Employee approved successfully')
      loadEmployees()
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Approval failed')
    }
  }

  async function reject(id: string) {
    try {
      await api.post(`/admin/users/${id}/reject`)
      toast.success('Request rejected')
      loadEmployees()
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Rejection failed')
    }
  }

  const filteredEmployees = filter === 'pending'
    ? employees.filter(e => e.approval_status === 'pending')
    : employees

  return (
    <div className="p-6 md:p-8 space-y-6 max-w-5xl w-full mx-auto overflow-y-auto scrollbar-thin">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--border-subtle)] pb-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-[--text-primary]">Employee Authorization</h1>
          <p className="text-xs text-[--text-muted] mt-0.5">
            Approve sign-ups and assign specific role-based permissions for your team.
          </p>
        </div>
        <Link href="/dashboard" className="text-xs text-[var(--accent-cyan)] hover:underline border border-[var(--accent-cyan)]/20 px-3 py-1.5 rounded-lg bg-[var(--accent-cyan)]/5 font-medium transition-all">
          ← Back to Workspace
        </Link>
      </div>

      {/* Super Admin Quick Link banner */}
      <div className="glass p-5 rounded-2xl border border-[var(--accent-cyan)]/20 bg-[var(--accent-cyan)]/[0.01] flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-card">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--accent-cyan)] mb-1">Super Admin Account Provisioner</h3>
          <p className="text-xs text-[--text-muted] leading-relaxed max-w-md">
            Skip approval workflows by creating pre-authorized user accounts directly with credentials, roles, and departments.
          </p>
        </div>
        <Link href="/dashboard/admin/super-admin" className="qs-btn-primary py-2.5 px-4 text-xs font-semibold text-center whitespace-nowrap cursor-pointer shadow-glow">
          Open Provisioning Panel
        </Link>
      </div>

      {/* Filters */}
      <div className="flex gap-2">
        <button
          className={filter === 'pending' ? 'qs-btn-primary text-xs font-medium cursor-pointer' : 'qs-btn-secondary text-xs font-medium cursor-pointer'}
          onClick={() => setFilter('pending')}
        >
          Pending Approval ({employees.filter(e => e.approval_status === 'pending').length})
        </button>
        <button
          className={filter === '' ? 'qs-btn-primary text-xs font-medium cursor-pointer' : 'qs-btn-secondary text-xs font-medium cursor-pointer'}
          onClick={() => setFilter('')}
        >
          All Users ({employees.length})
        </button>
      </div>

      {/* Employee List */}
      {loading ? (
        <div className="flex items-center gap-2 p-6 text-xs text-[--text-muted]">
          <span className="loading-dot"></span>
          <span className="loading-dot"></span>
          <span className="loading-dot"></span>
          Loading records...
        </div>
      ) : filteredEmployees.length === 0 ? (
        <div className="glass p-8 rounded-2xl text-center text-xs text-[--text-muted] border border-white/5 shadow-card">
          No employee records found in this list.
        </div>
      ) : (
        <div className="space-y-4">
          {filteredEmployees.map((e) => (
            <div key={e.id} className="glass p-5 rounded-2xl border border-white/5 shadow-card flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm text-[--text-primary]">{e.full_name || 'Anonymous User'}</span>
                  <span className={`text-[9px] font-bold uppercase px-2 py-0.5 rounded-full ${
                    e.approval_status === 'approved' ? 'bg-[var(--accent-green)]/15 text-[var(--accent-green)]' :
                    e.approval_status === 'pending' ? 'bg-[var(--accent-cyan)]/15 text-[var(--accent-cyan)]' :
                    'bg-[var(--accent-red)]/15 text-[var(--accent-red)]'
                  }`}>
                    {e.approval_status}
                  </span>
                </div>
                <div className="text-xs text-[--text-muted] mt-0.5 font-mono">{e.email}</div>
                {e.approval_status === 'approved' && (
                  <div className="text-[10px] text-[--text-muted] mt-1.5 flex gap-2">
                    <span className="bg-white/5 px-2 py-0.5 rounded">Role: {e.role}</span>
                    <span className="bg-white/5 px-2 py-0.5 rounded capitalize">Dept: {e.department}</span>
                  </div>
                )}
              </div>

              {e.approval_status === 'pending' && (
                <div className="flex flex-wrap items-center gap-2.5 bg-black/15 p-3 rounded-xl border border-white/5">
                  <div>
                    <label className="block text-[8px] font-semibold text-[--text-muted] uppercase mb-0.5 font-mono">Assign Role</label>
                    <select
                      className="qs-select text-xs py-1.5 px-2.5"
                      value={roleById[e.id] || 'viewer'}
                      onChange={(ev) => setRoleById((r) => ({ ...r, [e.id]: ev.target.value }))}
                    >
                      {ROLES.map((r) => (
                        <option key={r} value={r}>
                          {r}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-[8px] font-semibold text-[--text-muted] uppercase mb-0.5 font-mono">Assign Department</label>
                    <select
                      className="qs-select text-xs py-1.5 px-2.5"
                      value={deptById[e.id] || 'general'}
                      onChange={(ev) => setDeptById((d) => ({ ...d, [e.id]: ev.target.value }))}
                    >
                      {DEPARTMENTS.map((d) => (
                        <option key={d} value={d}>
                          {d}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="flex gap-1.5 self-end mt-1 sm:mt-0">
                    <button
                      className="qs-btn-primary py-1.5 px-3.5 text-xs font-semibold cursor-pointer shadow-glow"
                      onClick={() => approve(e.id)}
                    >
                      Approve
                    </button>
                    <button
                      className="qs-btn-ghost py-1.5 px-3.5 text-xs font-semibold cursor-pointer hover:bg-[var(--accent-red)]/10 hover:text-[var(--accent-red)] border border-white/5 hover:border-[var(--accent-red)]/20"
                      onClick={() => reject(e.id)}
                    >
                      Reject
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
