"use client"
import React from 'react'
import Link from 'next/link'
import useAuthStore from '../../lib/store'
import api from '../../lib/api'

export default function Sidebar(){
  const user = useAuthStore((s) => s.user)
  const setUser = useAuthStore((s) => s.setUser)

  React.useEffect(() => {
    if (user) return
    const token = typeof window !== 'undefined' ? localStorage.getItem('qs_token') : null
    if (!token) return
    api.get('/auth/me').then((r) => setUser(r.data)).catch(() => {})
  }, [user, setUser])

  return (
    <aside className="w-60 bg-[--bg-elevated] p-4 h-screen flex flex-col gap-4">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded flex items-center justify-center bg-[--accent-cyan] text-black font-bold">QS</div>
        <div>
          <div className="font-display">QuerySafe</div>
          <div className="text-xs text-[--text-muted]">v0.1</div>
        </div>
      </div>

      <div className="space-y-2">
        <div className="text-xs text-[--text-muted]">Connections</div>
        <div className="glass p-3 rounded">No DB connected</div>
      </div>

      <div className="mt-4">
        <div className="text-xs text-[--text-muted] mb-2">Recent queries</div>
        <div className="space-y-1 text-xs font-mono text-[--text-muted]">
          <div>SELECT * FROM invoices LIMIT 10</div>
          <div>SHOW TABLES</div>
          <div>SELECT id, name FROM customers</div>
        </div>
      </div>

      {user?.role === 'admin' && (
        <Link href="/dashboard/admin" className="text-sm text-[--accent-cyan] hover:underline">
          Manage employees
        </Link>
      )}

      <div className="mt-auto text-xs text-[--text-muted] capitalize">
        {user ? `${user.role} · ${user.department}` : 'Loading…'}
      </div>
    </aside>
  )
}
