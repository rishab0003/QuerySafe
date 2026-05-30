"use client"
import React, { useState } from 'react'
import Link from 'next/link'
import useAuthStore from '../../lib/store'
import { useChatStore } from '../../lib/store'
import api from '../../lib/api'

export default function Sidebar() {
  const user = useAuthStore((s) => s.user)
  const setUser = useAuthStore((s) => s.setUser)
  const connectionId = useChatStore((s) => s.connectionId)
  const schema = useChatStore((s) => s.schema)
  const [expandedTable, setExpandedTable] = useState<string | null>(null)

  React.useEffect(() => {
    if (user) return
    const token = typeof window !== 'undefined' ? localStorage.getItem('qs_token') : null
    if (!token) return
    api.get('/auth/me').then((r) => setUser(r.data)).catch(() => {})
  }, [user, setUser])

  const toggleTable = (tableName: string) => {
    setExpandedTable(expandedTable === tableName ? null : tableName)
  }

  return (
    <aside className="w-full lg:w-64 bg-[var(--bg-surface)] border-b lg:border-b-0 lg:border-r border-[var(--border-subtle)] p-4 lg:h-screen flex flex-col gap-4 select-none shrink-0 shadow-card">
      {/* Brand Header */}
      <Link href="/dashboard" className="flex items-center gap-3 mb-2 hover:opacity-95 transition-opacity">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-gradient-to-tr from-[var(--accent-cyan)] to-[var(--jade-dim)] text-black font-extrabold shadow-glow">
          QS
        </div>
        <div>
          <div className="font-display font-bold tracking-tight text-sm">QuerySafe</div>
          <div className="text-[10px] text-[--text-muted] font-medium tracking-wider uppercase">Enterprise NL-SQL</div>
        </div>
      </Link>

      {/* Database Connection Status Banner */}
      <div className="space-y-1.5">
        <div className="text-[10px] font-semibold text-[--text-muted] uppercase tracking-wider">Connection Status</div>
        {connectionId ? (
          <div className="glass p-3 rounded-xl border border-[var(--accent-green)]/20 bg-[var(--accent-green)]/[0.02] flex items-center gap-2.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--accent-green)] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--accent-green)]"></span>
            </span>
            <div className="truncate">
              <span className="text-xs font-semibold text-[--text-primary] block truncate">
                Active Session
              </span>
              <span className="text-[10px] text-[--text-muted] font-mono block truncate">
                {connectionId.slice(0, 16)}...
              </span>
            </div>
          </div>
        ) : (
          <div className="glass p-3 rounded-xl border border-[var(--accent-red)]/20 bg-[var(--accent-red)]/[0.02] flex items-center gap-2.5">
            <span className="h-2 w-2 rounded-full bg-[var(--accent-red)]"></span>
            <div>
              <span className="text-xs font-semibold text-[--text-primary] block">
                Disconnected
              </span>
              <span className="text-[10px] text-[--text-muted] block">
                Connect a DB to start querying
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Accordion Database Schema Inspector */}
      {connectionId && schema && schema.tables && (
        <div className="flex-1 flex flex-col min-h-0 space-y-1.5 max-h-72 lg:max-h-none">
          <div className="text-[10px] font-semibold text-[--text-muted] uppercase tracking-wider">
            Schema Explorer
          </div>
          <div className="flex-1 overflow-y-auto scrollbar-thin bg-black/5 dark:bg-black/15 border border-[var(--border-subtle)] rounded-xl p-2 space-y-1 max-h-64 lg:max-h-none">
            {schema.tables.map((t: any) => {
              const isOpen = expandedTable === t.name
              return (
                <div key={t.name} className="rounded-lg overflow-hidden transition-all bg-transparent hover:bg-black/5 dark:hover:bg-white/[0.03]">
                  <button
                    onClick={() => toggleTable(t.name)}
                    className="w-full flex items-center justify-between p-2 text-left font-mono text-[11px] text-[--text-primary]"
                  >
                    <span className="truncate flex items-center gap-1.5 font-medium">
                      <span className="text-[var(--accent-cyan)] font-sans">⊞</span> {t.name}
                    </span>
                    <span className="text-[10px] text-[--text-muted] font-sans">
                      {isOpen ? '▲' : '▼'}
                    </span>
                  </button>
                  {isOpen && (
                    <div className="px-3 pb-2 pt-0.5 border-t border-[var(--border-subtle)] bg-black/5 dark:bg-black/20 space-y-1">
                      {t.columns.map((c: any) => (
                        <div key={c.name} className="flex justify-between font-mono text-[9px] text-[--text-muted]">
                          <span className="truncate text-[--text-primary] dark:text-white/70">{c.name}</span>
                          <span className="text-[var(--accent-cyan)] font-light">{c.type.toLowerCase()}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Static recent queries fallback */}
      {!schema && (
        <div className="mt-2 lg:mt-0">
          <div className="text-[10px] font-semibold text-[--text-muted] uppercase tracking-wider mb-1.5">
            Databases
          </div>
          <div className="flex items-center gap-2 mb-3">
            <div className="flex-1 space-y-1 bg-black/5 dark:bg-black/15 p-2.5 rounded-xl border border-[var(--border-subtle)] text-[10px]">
              <div className="flex items-center justify-between">
                <div className="font-medium">Demo DB Available</div>
                <div className="text-[10px] font-mono text-[--text-muted]">1 DB</div>
              </div>
              <div className="text-[9px] text-[--text-muted]">Small demo sqlite DB with sample tables (sales, employees, signups)</div>
            </div>
            <button
              onClick={() => {
                // Quick-connect demo database locally (client-side demo)
                useChatStore.getState().setConnectionId('demo-local')
                useChatStore.getState().setSchema({ tables: [
                  { name: 'sales', columns: [{ name: 'city', type: 'TEXT' }, { name: 'total_price', type: 'REAL' }, { name: 'product_category', type: 'TEXT' }, { name: 'customer_type', type: 'TEXT' }] },
                  { name: 'employees', columns: [{ name: 'id', type: 'TEXT' }, { name: 'email', type: 'TEXT' }, { name: 'full_name', type: 'TEXT' }] },
                  { name: 'signups', columns: [{ name: 'day', type: 'TEXT' }, { name: 'count', type: 'INTEGER' }] }
                ] })
              }}
              className="px-3 py-2 text-xs font-medium bg-[var(--accent-cyan)] text-white rounded-lg shadow-sm"
            >
              Connect Demo
            </button>
          </div>

          <div className="text-[10px] font-semibold text-[--text-muted] uppercase tracking-wider mb-1.5">
            Sample DB Queries
          </div>
          <div className="space-y-1 bg-black/5 dark:bg-black/15 p-2.5 rounded-xl border border-[var(--border-subtle)] text-[10px] font-mono text-[--text-muted]">
            <div className="truncate border-b border-[var(--border-subtle)] pb-1">SELECT * FROM sales LIMIT 5</div>
            <div className="truncate border-b border-[var(--border-subtle)] py-1">SELECT COUNT(*) FROM products</div>
            <div className="truncate pt-1">SELECT * FROM employees</div>
          </div>
        </div>
      )}

      {/* Nav Links */}
      <div className="space-y-1">
        <div className="text-[10px] font-semibold text-[--text-muted] uppercase tracking-wider mb-1.5">
          Navigation
        </div>
        <Link
          href="/dashboard"
          className="flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium hover:bg-black/5 dark:hover:bg-white/5 transition-all text-[--text-primary]"
        >
          <span>💬</span> AI Workspace
        </Link>
        <Link
          href="/dashboard/charts"
          className="flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-medium hover:bg-black/5 dark:hover:bg-white/5 transition-all text-[--text-primary]"
        >
          <span>📊</span> Dynamic Dashboards
        </Link>

        {user?.role === 'admin' && (
          <div className="pt-2 border-t border-[var(--border-subtle)] space-y-1">
            <Link
              href="/dashboard/admin"
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium text-[var(--accent-cyan)] hover:bg-[var(--accent-cyan)]/10 transition-all"
            >
              <span>⚙️</span> Access Approvals
            </Link>
            <Link
              href="/dashboard/admin/super-admin"
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium text-[var(--accent-cyan)] hover:bg-[var(--accent-cyan)]/10 transition-all"
            >
              <span>🛡️</span> Super Admin Panel
            </Link>
          </div>
        )}
      </div>

      {/* User Info footer */}
      <div className="mt-auto pt-3 border-t border-[var(--border-subtle)] flex items-center justify-between gap-3">
        <div className="min-w-0">
          <div className="text-xs font-semibold text-[--text-primary] truncate">{user?.full_name || 'Loading user...'}</div>
          <div className="text-[10px] text-[--text-muted] font-medium uppercase tracking-wider truncate">
            {user ? `${user.role} · ${user.department}` : 'Loading...'}
          </div>
        </div>
        <button
          onClick={() => {
            useAuthStore.getState().logout()
            window.location.href = '/auth/login'
          }}
          className="text-xs p-1 text-[var(--accent-red)] hover:bg-[var(--accent-red)]/10 rounded transition-all cursor-pointer"
          title="Sign Out"
        >
          🚪
        </button>
      </div>
    </aside>
  )
}
