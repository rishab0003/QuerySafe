"use client"
import React, { useState, useRef, useEffect } from 'react'
import api from '../../lib/api'
import useAuthStore, { useChatStore } from '../../lib/store'
import ResultTable from './ResultTable'
import DBConnector from './DBConnector'
import toast from 'react-hot-toast'

export default function ChatPanel() {
  const user = useAuthStore((s) => s.user)
  const connectionId = useChatStore((s) => s.connectionId)
  const sessionId = useChatStore((s) => s.sessionId)
  const messages = useChatStore((s) => s.messages)
  const addMessage = useChatStore((s) => s.addMessage)
  const clearMessages = useChatStore((s) => s.clearMessages)

  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)
  const chatEndRef = useRef<HTMLDivElement | null>(null)

  // Auto-scroll chat history
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function send() {
    if (!prompt.trim() || !connectionId) return
    const currentPrompt = prompt
    setPrompt('')
    setLoading(true)
    setErrorMsg(null)

    // Append User Message
    const userMsg = {
      id: `msg_${Date.now()}_user`,
      role: 'user' as const,
      text: currentPrompt,
      timestamp: Date.now(),
    }
    addMessage(userMsg)

    try {
      const res = await api.post('/ai/query', {
        user_prompt: currentPrompt,
        connection_id: connectionId,
        session_id: sessionId,
        role: user?.role || 'viewer',
      })

      const data = res.data

      // Append Agent Message on success
      const agentMsg = {
        id: `msg_${Date.now()}_agent`,
        role: 'agent' as const,
        text: data.reasoning || 'Query executed successfully.',
        sql: data.sql_generated,
        confidence: data.confidence_score,
        tablesUsed: data.tables_used,
        reasoning: data.reasoning,
        results: data.results,
        rowCount: data.row_count,
        queryTimeMs: data.query_time_ms,
        timestamp: Date.now(),
      }
      addMessage(agentMsg)
    } catch (err: any) {
      console.error(err)
      const errDetail = err?.response?.data?.detail
      let detailedMsg = err?.response?.data?.detail || err?.message || 'Failed to get query results'

      // Check if it is a security/RBAC violation (returned as object by FastAPI backend)
      if (errDetail && typeof errDetail === 'object') {
        const securityMsg = {
          id: `msg_${Date.now()}_agent`,
          role: 'agent' as const,
          text: errDetail.message || 'Security validation failed.',
          sql: errDetail.sql_generated || null,
          isBlocked: true,
          blockedKeywords: errDetail.blocked_keywords || [],
          timestamp: Date.now(),
        }
        addMessage(securityMsg)
      } else {
        toast.error(detailedMsg)
        setErrorMsg(detailedMsg)
      }
    } finally {
      setLoading(false)
    }
  }

  function handleExplainInInspector(sql: string) {
    localStorage.setItem('qs_last_sql', sql)
    window.dispatchEvent(new Event('qs_sql_update'))
    toast.success('Loaded query into SQL Inspector')
  }

  // Render Splash Setup Screen if disconnected
  if (!connectionId) {
    return (
      <div className="flex-1 overflow-auto bg-[var(--bg-void)] flex items-center justify-center p-6 select-none animate-fade-in">
        <div className="max-w-md w-full space-y-6 text-center">
          <div className="space-y-2">
            <div className="inline-flex p-3 rounded-2xl bg-gradient-to-tr from-[var(--accent-cyan)]/10 to-[var(--jade-subtle)] border border-[var(--accent-cyan)]/20 shadow-glow mb-2 text-3xl">
              🛡️
            </div>
            <h2 className="text-2xl font-display font-bold tracking-tight text-[--text-primary]">
              Connect to QuerySafe
            </h2>
            <p className="text-xs text-[--text-muted] leading-relaxed max-w-sm mx-auto">
              QuerySafe acts as an intelligent, role-authorized broker between you and your database. Complete the connection below to start querying with natural language.
            </p>
          </div>
          <DBConnector />
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col h-screen min-h-0 bg-[var(--bg-void)]">
      {/* Top Header info */}
      <header className="px-6 py-4 border-b border-[var(--border-subtle)] flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold text-[--text-primary]">AI Assistant Workspace</h2>
          <div className="text-[10px] text-[--text-muted]">
            Enforcing RBAC rules for <span className="text-[var(--accent-cyan)] font-mono">{user?.role}</span>
          </div>
        </div>
        <button
          onClick={clearMessages}
          className="text-xs text-[--text-muted] hover:text-[var(--accent-red)] transition-colors px-2 py-1 rounded hover:bg-black/5 dark:hover:bg-white/5 border border-[var(--border-subtle)]"
        >
          Clear History
        </button>
      </header>

      {/* Message Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center space-y-3 opacity-60">
            <div className="text-3xl">🤖</div>
            <div className="text-sm font-medium text-[--text-secondary]">How can I help you today?</div>
            <p className="text-xs text-[--text-muted] max-w-xs leading-relaxed">
              Ask database questions like "Show me all transactions from sales department" or "What products have low stock?"
            </p>
          </div>
        ) : (
          messages.map((m: any) => {
            const isUser = m.role === 'user'
            return (
              <div key={m.id} className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
                <div className={`max-w-[85%] rounded-2xl p-4 ${isUser ? 'bg-gradient-to-tr from-[var(--jade)] to-[var(--jade-dim)] text-black shadow-card font-medium' : 'glass-elevated border border-[var(--border-subtle)] shadow-elevated'} space-y-3`}>
                  {/* Text Description */}
                  <p className="text-xs leading-relaxed whitespace-pre-wrap">{m.text}</p>

                  {/* Security / Block Warning */}
                  {m.isBlocked && (
                    <div className="border border-[var(--accent-red)]/30 bg-[var(--accent-red)]/10 p-3 rounded-xl space-y-2">
                      <div className="flex items-center gap-2 text-xs font-semibold text-[var(--accent-red)]">
                        <span>⚠️</span> SECURITY EXCLUSION TRIGGERED
                      </div>
                      <p className="text-[11px] text-[--text-muted] leading-relaxed">
                        This statement was blocked. Policy forbids mutating operations (INSERT, UPDATE, DELETE) or database role-based table violations.
                      </p>
                      {m.blockedKeywords && m.blockedKeywords.length > 0 && (
                        <div className="flex gap-1.5 flex-wrap">
                          {m.blockedKeywords.map((kw: string) => (
                            <span key={kw} className="text-[9px] font-mono px-2 py-0.5 bg-[var(--accent-red)]/20 text-[var(--accent-red)] rounded border border-[var(--accent-red)]/20">
                              {kw}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* SQL Output Box */}
                  {m.sql && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-[10px] text-[--text-muted] font-medium uppercase tracking-wider">
                        <span>Generated SQL</span>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleExplainInInspector(m.sql)}
                            className="text-[var(--accent-cyan)] hover:underline cursor-pointer"
                          >
                            Explain in Inspector
                          </button>
                        </div>
                      </div>
                      <pre className="sql-block max-h-48 overflow-auto scrollbar-thin text-xs font-mono">{m.sql}</pre>
                    </div>
                  )}

                  {/* Execution Performance Badges */}
                  {!isUser && !m.isBlocked && (m.confidence !== undefined || m.queryTimeMs !== undefined) && (
                    <div className="flex gap-2 flex-wrap pt-1">
                      {m.confidence !== undefined && (
                        <span className="qs-chip qs-chip-jade text-[10px]">
                          🎯 Confidence: {Math.round(m.confidence * 100)}%
                        </span>
                      )}
                      {m.queryTimeMs !== undefined && (
                        <span className="qs-chip text-[10px]">
                          ⚡ {m.queryTimeMs}ms
                        </span>
                      )}
                      {m.rowCount !== undefined && (
                        <span className="qs-chip text-[10px]">
                          📋 {m.rowCount} Rows
                        </span>
                      )}
                    </div>
                  )}

                  {/* Results Display */}
                  {m.results && m.results.length > 0 && (
                    <div className="mt-2.5">
                      <ResultTable
                        columns={Object.keys(m.results[0])}
                        rows={m.results}
                      />
                    </div>
                  )}
                </div>
              </div>
            )
          })
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="glass p-4 rounded-2xl flex items-center gap-3">
              <span className="text-xs text-[--text-muted]">AI is compiling schema & generating query</span>
              <div className="flex gap-1.5">
                <span className="loading-dot"></span>
                <span className="loading-dot"></span>
                <span className="loading-dot"></span>
              </div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Box */}
      <footer className="p-4 border-t border-[var(--border-subtle)] bg-[var(--bg-surface)]">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            send()
          }}
          className="flex gap-3 items-center max-w-4xl mx-auto"
        >
          <input
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={loading}
            className="qs-input flex-1 py-3 px-4 rounded-xl text-sm"
            placeholder="Type your data question (e.g. 'Show me products by category')..."
          />
          <button
            type="submit"
            disabled={loading || !prompt.trim()}
            className="qs-btn-primary py-3 px-5 font-semibold text-sm cursor-pointer shadow-glow"
          >
            {loading ? 'Executing' : 'Run Query'}
          </button>
        </form>
      </footer>
    </div>
  )
}
