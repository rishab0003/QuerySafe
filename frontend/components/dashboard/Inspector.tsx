"use client"
import React, { useState, useEffect } from 'react'
import api from '../../lib/api'
import useAuthStore, { useChatStore } from '../../lib/store'
import ResultTable from './ResultTable'
import toast from 'react-hot-toast'

export default function Inspector() {
  const user = useAuthStore((s) => s.user)
  const connectionId = useChatStore((s) => s.connectionId)

  const [sql, setSql] = useState<string>('')
  const [explainData, setExplainData] = useState<{
    explanation: string
    why_these_tables: string
    assumptions_made: string
  } | null>(null)
  const [explainLoading, setExplainLoading] = useState(false)

  const [runLoading, setRunLoading] = useState(false)
  const [runResults, setRunResults] = useState<any[] | null>(null)
  const [runColumns, setRunColumns] = useState<string[] | null>(null)

  // Listen for SQL updates from other components (like ChatPanel)
  useEffect(() => {
    try {
      const last = localStorage.getItem('qs_last_sql')
      if (last) setSql(last)
    } catch (e) {}

    const handleUpdate = () => {
      try {
        const last = localStorage.getItem('qs_last_sql')
        if (last) {
          setSql(last)
          // Reset previous results
          setExplainData(null)
          setRunResults(null)
        }
      } catch (e) {}
    }
    window.addEventListener('qs_sql_update', handleUpdate)
    return () => window.removeEventListener('qs_sql_update', handleUpdate)
  }, [])

  async function explainSql() {
    if (!sql.trim()) return toast.error('No SQL statement to explain.')
    setExplainLoading(true)
    setExplainData(null)
    try {
      const res = await api.post('/ai/explain', {
        sql: sql,
        user_prompt: 'Manual statement inspection',
      })
      setExplainData(res.data)
      toast.success('Generated AI explanation')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || err?.message || 'Failed to explain SQL')
    } finally {
      setExplainLoading(false)
    }
  }

  async function runSql() {
    if (!sql.trim()) return toast.error('No SQL statement to run.')
    if (!connectionId) return toast.error('Please connect to a database first.')
    setRunLoading(true)
    setRunResults(null)
    setRunColumns(null)

    try {
      const res = await api.post('/database/execute', {
        connection_id: connectionId,
        sql: sql,
        role: user?.role || 'viewer',
      })
      const data = res.data
      setRunResults(data.rows)
      if (data.rows.length > 0) {
        setRunColumns(Object.keys(data.rows[0]))
      }
      toast.success(`Query returned ${data.row_count} rows in ${data.execution_time_ms}ms`)
    } catch (err: any) {
      const detail = err?.response?.data?.detail
      toast.error(typeof detail === 'string' ? detail : err?.message || 'Query execution failed')
    } finally {
      setRunLoading(false)
    }
  }

  return (
    <aside className="w-96 bg-[var(--bg-surface)] border-l border-[var(--border-subtle)] p-5 h-screen overflow-y-auto scrollbar-thin flex flex-col gap-4 shrink-0 shadow-card">
      <div className="flex items-center justify-between pb-2 border-b border-[var(--border-subtle)]">
        <h2 className="text-sm font-semibold tracking-wider uppercase text-[--text-muted]">SQL Console</h2>
        <span className="text-[10px] font-semibold bg-[var(--accent-cyan)]/10 text-[var(--accent-cyan)] px-2 py-0.5 rounded-full font-mono">
          Interactive
        </span>
      </div>

      {/* SQL Editor Area */}
      <div className="space-y-1.5 flex flex-col">
        <label className="text-[11px] font-semibold text-[--text-muted] uppercase tracking-wider">SQL Statement</label>
        <textarea
          value={sql}
          onChange={(e) => setSql(e.target.value)}
          className="w-full font-mono text-xs p-3.5 bg-black/35 text-[var(--accent-cyan)] rounded-xl border border-white/5 outline-none focus:border-[var(--accent-cyan)]/30 focus:shadow-glow scrollbar-thin"
          rows={7}
          placeholder="-- Enter or edit SQL here..."
        />
      </div>

      {/* Console Actions */}
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={explainSql}
          disabled={explainLoading || !sql.trim()}
          className="qs-btn-secondary py-2.5 text-xs font-semibold cursor-pointer border border-[var(--accent-cyan)]/20 hover:bg-[var(--accent-cyan)]/5"
        >
          {explainLoading ? 'Explaining...' : 'Explain Statement'}
        </button>
        <button
          onClick={runSql}
          disabled={runLoading || !sql.trim()}
          className="qs-btn-primary py-2.5 text-xs font-semibold cursor-pointer shadow-glow"
        >
          {runLoading ? 'Running...' : 'Execute Statement'}
        </button>
      </div>

      {/* AI Explanation Result Cards */}
      {explainData && (
        <div className="space-y-4 pt-2 animate-fade-in">
          <div className="glass p-4 rounded-xl border border-[var(--accent-cyan)]/10 bg-[var(--accent-cyan)]/[0.01] space-y-2">
            <h4 className="text-[10px] font-semibold text-[var(--accent-cyan)] uppercase tracking-wider">AI Translation</h4>
            <p className="text-xs text-[--text-primary] leading-relaxed">{explainData.explanation}</p>
          </div>

          <div className="glass p-4 rounded-xl border border-white/5 space-y-2">
            <h4 className="text-[10px] font-semibold text-[--text-muted] uppercase tracking-wider font-mono">Tables & Collections Used</h4>
            <p className="text-xs text-[--text-secondary] leading-relaxed">{explainData.why_these_tables}</p>
          </div>

          <div className="glass p-4 rounded-xl border border-white/5 space-y-2">
            <h4 className="text-[10px] font-semibold text-[--text-muted] uppercase tracking-wider font-mono">Assumptions Made</h4>
            <p className="text-xs text-[--text-secondary] leading-relaxed font-mono">{explainData.assumptions_made}</p>
          </div>
        </div>
      )}

      {/* Live Manual Execution Results */}
      {runResults !== null && (
        <div className="space-y-2 pt-2 flex-1 flex flex-col min-h-0 animate-fade-in">
          <div className="flex items-center justify-between">
            <h4 className="text-[10px] font-semibold text-[--text-muted] uppercase tracking-wider">Query Output</h4>
            <span className="text-[10px] text-[--text-muted]">{runResults.length} records returned</span>
          </div>

          {runResults.length === 0 ? (
            <div className="bg-black/15 border border-white/5 p-4 rounded-xl text-center text-xs text-[--text-muted]">
              No rows returned.
            </div>
          ) : (
            <div className="flex-1 overflow-auto border border-white/5 rounded-xl bg-black/15 p-2 scrollbar-thin max-h-80">
              {runColumns && (
                <ResultTable
                  columns={runColumns}
                  rows={runResults}
                />
              )}
            </div>
          )}
        </div>
      )}
    </aside>
  )
}
