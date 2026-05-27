"use client"
import React, { useState, useEffect } from 'react'
import api from '../../lib/api'
import { useChatStore } from '../../lib/store'
import toast from 'react-hot-toast'

export default function DBConnector() {
  const connectionId = useChatStore((s) => s.connectionId)
  const setConnectionId = useChatStore((s) => s.setConnectionId)
  const setSchema = useChatStore((s) => s.setSchema)

  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    type: 'postgres',
    host: 'postgres',
    port: 5432,
    user: 'postgres',
    password: 'secure-postgres-pass',
    database: 'querysafe',
  })

  // Load schema automatically if connectionId exists on mount
  useEffect(() => {
    if (connectionId) {
      loadSchema(connectionId)
    }
  }, [connectionId])

  async function loadSchema(connId: string) {
    try {
      const res = await api.get(`/database/schema/${connId}`)
      setSchema(res.data)
    } catch (err: any) {
      toast.error('Failed to load database schema details.')
    }
  }

  async function handleConnect(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await api.post('/database/connect', form)
      const connId = res.data.connection_id
      setConnectionId(connId)
      toast.success('Successfully connected to database!')
      await loadSchema(connId)
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Failed to connect. Verify your credentials.')
    } finally {
      setLoading(false)
    }
  }

  async function handleDisconnect() {
    if (!connectionId) return
    setLoading(true)
    try {
      await api.delete(`/database/disconnect/${connectionId}`)
      setConnectionId(null)
      setSchema(null)
      toast.success('Disconnected from database.')
    } catch (err: any) {
      // Clean up locally even if request fails
      setConnectionId(null)
      setSchema(null)
      toast.error('Disconnection completed locally.')
    } finally {
      setLoading(false)
    }
  }

  function applyPreset() {
    setForm({
      type: 'postgres',
      host: 'postgres',
      port: 5432,
      user: 'postgres',
      password: 'secure-postgres-pass',
      database: 'querysafe',
    })
    toast.success('Applied Postgres preset')
  }

  if (connectionId) {
    return (
      <div className="glass p-5 rounded-2xl border border-[var(--accent-cyan)]/20 shadow-glow space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--accent-green)] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--accent-green)]"></span>
            </span>
            <h3 className="font-semibold text-sm tracking-wider uppercase text-[var(--accent-cyan)]">Database Connected</h3>
          </div>
          <span className="text-xs font-mono bg-white/5 px-2 py-0.5 rounded text-[--text-muted]">
            ID: {connectionId.slice(0, 8)}...
          </span>
        </div>

        <div className="grid grid-cols-2 gap-3 text-xs bg-black/25 p-3 rounded-xl border border-white/5 font-mono">
          <div>
            <span className="text-[--text-muted] block">TYPE</span>
            <span className="text-[--text-primary] capitalize">{form.type}</span>
          </div>
          <div>
            <span className="text-[--text-muted] block">HOST</span>
            <span className="text-[--text-primary]">{form.host}</span>
          </div>
          <div>
            <span className="text-[--text-muted] block">DATABASE</span>
            <span className="text-[--text-primary]">{form.database}</span>
          </div>
          <div>
            <span className="text-[--text-muted] block">USER</span>
            <span className="text-[--text-primary]">{form.user}</span>
          </div>
        </div>

        <button
          onClick={handleDisconnect}
          disabled={loading}
          className="w-full py-2.5 rounded-lg text-xs font-medium border border-[var(--accent-red)]/30 hover:bg-[var(--accent-red)]/10 text-[var(--accent-red)] transition-all cursor-pointer"
        >
          {loading ? 'Disconnecting...' : 'Disconnect Database Session'}
        </button>
      </div>
    )
  }

  return (
    <div className="glass p-6 rounded-2xl shadow-card space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-sm tracking-wider uppercase text-[--text-muted]">Configure Connection</h3>
        <button
          type="button"
          onClick={applyPreset}
          className="text-[10px] uppercase font-semibold text-[var(--accent-cyan)] hover:underline border border-[var(--accent-cyan)]/20 px-2 py-1 rounded bg-[var(--accent-cyan)]/5"
        >
          Use Local Preset
        </button>
      </div>

      <form onSubmit={handleConnect} className="space-y-3">
        <div>
          <label className="block text-[11px] font-semibold text-[--text-muted] uppercase mb-1">Database Type</label>
          <select
            value={form.type}
            onChange={(e) => setForm({ ...form, type: e.target.value })}
            className="qs-select w-full"
          >
            <option value="postgres">PostgreSQL</option>
            <option value="mysql">MySQL (Connector)</option>
            <option value="mongodb">MongoDB (PyMongo)</option>
          </select>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <label className="block text-[11px] font-semibold text-[--text-muted] uppercase mb-1">Host</label>
            <input
              type="text"
              required
              className="qs-input w-full"
              value={form.host}
              onChange={(e) => setForm({ ...form, host: e.target.value })}
              placeholder="e.g. postgres"
            />
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-[--text-muted] uppercase mb-1">Port</label>
            <input
              type="number"
              required
              className="qs-input w-full"
              value={form.port}
              onChange={(e) => setForm({ ...form, port: parseInt(e.target.value) || 0 })}
              placeholder="5432"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-[11px] font-semibold text-[--text-muted] uppercase mb-1">Username</label>
            <input
              type="text"
              required
              className="qs-input w-full"
              value={form.user}
              onChange={(e) => setForm({ ...form, user: e.target.value })}
              placeholder="postgres"
            />
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-[--text-muted] uppercase mb-1">Database Name</label>
            <input
              type="text"
              required
              className="qs-input w-full"
              value={form.database}
              onChange={(e) => setForm({ ...form, database: e.target.value })}
              placeholder="querysafe"
            />
          </div>
        </div>

        <div>
          <label className="block text-[11px] font-semibold text-[--text-muted] uppercase mb-1">Password</label>
          <input
            type="password"
            required
            className="qs-input w-full font-mono"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            placeholder="••••••••••••"
          />
        </div>

        <button
          type="submit"
          disabled={loading}
          className="qs-btn-primary w-full py-2.5 mt-2 flex items-center justify-center font-medium"
        >
          {loading ? (
            <div className="flex items-center gap-1">
              <span className="loading-dot"></span>
              <span className="loading-dot"></span>
              <span className="loading-dot"></span>
            </div>
          ) : (
            'Establish Connection'
          )}
        </button>
      </form>
    </div>
  )
}
