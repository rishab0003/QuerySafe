"use client"
import React from 'react'
import { useRouter } from 'next/navigation'
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

const ROLES = ['viewer', 'hr', 'finance', 'sales', 'support']
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
      await loadEmployees()
    } catch {
      router.replace('/auth/login')
    }
  }

  async function loadEmployees() {
    setLoading(true)
    try {
      const q = filter ? `?status_filter=${filter}` : ''
      const res = await api.get(`/admin/users${q}`)
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

  React.useEffect(() => {
    if (user?.role === 'admin') loadEmployees()
  }, [filter, user?.role])

  async function approve(id: string) {
    try {
      await api.post(`/admin/users/${id}/approve`, {
        role: roleById[id] || 'viewer',
        department: deptById[id] || 'general',
      })
      toast.success('Employee approved')
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

  return (
    <div className="min-h-screen bg-[--bg-void] text-[--text-primary] p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-display">Employee authorization</h1>
            <p className="text-sm text-[--text-muted] mt-1">
              Approve sign-ups and assign roles for your team.
            </p>
          </div>
          <a href="/dashboard" className="text-sm text-ink-300 hover:text-white">
            ← Back to dashboard
          </a>
        </div>

        <div className="flex gap-2 mb-6">
          <button
            className={filter === 'pending' ? 'qs-btn-primary' : 'qs-btn-secondary'}
            onClick={() => setFilter('pending')}
          >
            Pending
          </button>
          <button
            className={filter === '' ? 'qs-btn-primary' : 'qs-btn-secondary'}
            onClick={() => setFilter('')}
          >
            All
          </button>
        </div>

        {loading ? (
          <p className="text-[--text-muted]">Loading…</p>
        ) : employees.length === 0 ? (
          <div className="glass p-6 rounded-lg text-[--text-muted]">No employees in this list.</div>
        ) : (
          <div className="space-y-4">
            {employees.map((e) => (
              <div key={e.id} className="glass p-4 rounded-lg flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <div className="font-medium">{e.full_name || e.email}</div>
                  <div className="text-sm text-[--text-muted]">{e.email}</div>
                  <div className="text-xs mt-1 capitalize">
                    Status: <span className="text-ink-200">{e.approval_status}</span>
                    {e.role && e.approval_status === 'approved' && (
                      <> · Role: {e.role}</>
                    )}
                  </div>
                </div>
                {e.approval_status === 'pending' && (
                  <div className="flex flex-wrap items-center gap-2">
                    <select
                      className="qs-input text-sm py-1"
                      value={roleById[e.id] || 'viewer'}
                      onChange={(ev) => setRoleById((r) => ({ ...r, [e.id]: ev.target.value }))}
                    >
                      {ROLES.map((r) => (
                        <option key={r} value={r}>
                          {r}
                        </option>
                      ))}
                    </select>
                    <select
                      className="qs-input text-sm py-1"
                      value={deptById[e.id] || 'general'}
                      onChange={(ev) => setDeptById((d) => ({ ...d, [e.id]: ev.target.value }))}
                    >
                      {DEPARTMENTS.map((d) => (
                        <option key={d} value={d}>
                          {d}
                        </option>
                      ))}
                    </select>
                    <button className="qs-btn-primary text-sm" onClick={() => approve(e.id)}>
                      Approve
                    </button>
                    <button className="qs-btn-secondary text-sm" onClick={() => reject(e.id)}>
                      Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
