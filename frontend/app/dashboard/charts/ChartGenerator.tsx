"use client"
import React, { useState, useEffect } from 'react'
import {
  ResponsiveContainer,
  LineChart, Line,
  BarChart, Bar,
  AreaChart, Area,
  PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, Legend
} from 'recharts'
import api from '../../../lib/api'
import useAuthStore, { useChatStore } from '../../../lib/store'
import toast from 'react-hot-toast'

interface ChartSpec {
  type: 'LineChart' | 'BarChart' | 'PieChart' | 'AreaChart'
  title: string
  sql: string
  x_axis: string
  y_axis: string
  color: string
  description: string
}

interface LoadedChart {
  spec: ChartSpec
  data: any[]
  loading: boolean
  error: string | null
}

const DEMO_DASHBOARDS = [
  {
    name: "Sales & Financials",
    prompt: "Monthly billing summary and sales performance",
    charts: [
      {
        type: "AreaChart" as const,
        title: "Monthly Invoiced Amounts",
        sql: "SELECT month, amount FROM invoice_summary",
        x_axis: "month",
        y_axis: "amount",
        color: "#00E5FF",
        description: "Aggregated monthly billing invoice volumes showing overall growth trend.",
        data: [
          { month: "Jan", amount: 42000 },
          { month: "Feb", amount: 48000 },
          { month: "Mar", amount: 51200 },
          { month: "Apr", amount: 62000 },
          { month: "May", amount: 79000 },
          { month: "Jun", amount: 95000 }
        ]
      },
      {
        type: "BarChart" as const,
        title: "Product Category Revenue",
        sql: "SELECT category, revenue FROM product_sales",
        x_axis: "category",
        y_axis: "revenue",
        color: "#00C896",
        description: "Direct comparisons of revenue generated across key product groupings.",
        data: [
          { category: "Cloud Security", revenue: 145000 },
          { category: "Network Firewalls", revenue: 89000 },
          { category: "Audit & Log Compliance", revenue: 112000 },
          { category: "Database Obfuscator", revenue: 76000 }
        ]
      },
      {
        type: "LineChart" as const,
        title: "Customer Support Resolution Times",
        sql: "SELECT week, hours FROM support_sla",
        x_axis: "week",
        y_axis: "hours",
        color: "#FFA726",
        description: "Average duration in hours to successfully close client escalated tickets.",
        data: [
          { week: "W1", hours: 4.8 },
          { week: "W2", hours: 4.2 },
          { week: "W3", hours: 3.9 },
          { week: "W4", hours: 3.5 },
          { week: "W5", hours: 3.1 },
          { week: "W6", hours: 2.8 }
        ]
      },
      {
        type: "PieChart" as const,
        title: "Lead Acquisition Channels",
        sql: "SELECT channel, count FROM lead_sources",
        x_axis: "channel",
        y_axis: "count",
        color: "#EC407A",
        description: "Distribution of inbound enterprise leads by marketing segment.",
        data: [
          { channel: "Organic Search", count: 480 },
          { channel: "Partner Referrals", count: 290 },
          { channel: "Tech Webinars", count: 180 },
          { channel: "Direct Outreach", count: 90 }
        ]
      }
    ]
  },
  {
    name: "Employee Demographics",
    prompt: "Show headcount and department distributions",
    charts: [
      {
        type: "BarChart" as const,
        title: "Headcount by Department",
        sql: "SELECT department, headcount FROM employees_count",
        x_axis: "department",
        y_axis: "headcount",
        color: "#00E5FF",
        description: "Active full-time equivalent staffing records per team.",
        data: [
          { department: "Engineering", headcount: 84 },
          { department: "Sales", headcount: 45 },
          { department: "Customer Success", headcount: 31 },
          { department: "Product & Design", headcount: 18 },
          { department: "Finance & Admin", headcount: 12 }
        ]
      },
      {
        type: "PieChart" as const,
        title: "Employee Security Clearance",
        sql: "SELECT clearance, ratio FROM employee_clearances",
        x_axis: "clearance",
        y_axis: "ratio",
        color: "#00C896",
        description: "RBAC access distributions for corporate data assets.",
        data: [
          { clearance: "Viewer", ratio: 65 },
          { clearance: "Approver", ratio: 25 },
          { clearance: "Super Admin", ratio: 10 }
        ]
      }
    ]
  }
]

export default function ChartGenerator() {
  const user = useAuthStore((s) => s.user)
  const connectionId = useChatStore((s) => s.connectionId)

  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [isDemoMode, setIsDemoMode] = useState(!connectionId)
  const [dashboardTitle, setDashboardTitle] = useState('Workspace Dashboards')
  const [charts, setCharts] = useState<LoadedChart[]>([])
  const [isDarkTheme, setIsDarkTheme] = useState(true)

  // Detect theme class on document element
  useEffect(() => {
    const checkTheme = () => {
      const isDark = document.documentElement.classList.contains('dark')
      setIsDarkTheme(isDark)
    }
    checkTheme()

    const observer = new MutationObserver(checkTheme)
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => observer.disconnect()
  }, [])

  // Automatically switch mode if connection state changes
  useEffect(() => {
    if (connectionId) {
      setIsDemoMode(false)
    } else {
      setIsDemoMode(true)
    }
  }, [connectionId])

  // Load a demo dashboard preset
  function loadDemo(preset: typeof DEMO_DASHBOARDS[0]) {
    setDashboardTitle(`${preset.name} (Demo Mode)`)
    setPrompt(preset.prompt)
    const formatted = preset.charts.map((c) => ({
      spec: {
        type: c.type,
        title: c.title,
        sql: c.sql,
        x_axis: c.x_axis,
        y_axis: c.y_axis,
        color: c.color,
        description: c.description
      },
      data: c.data,
      loading: false,
      error: null
    }))
    setCharts(formatted)
    toast.success(`Loaded ${preset.name} Dashboard`)
  }

  // Generate dynamic dashboard from prompt
  async function generateDashboard(e: React.FormEvent) {
    e.preventDefault()
    if (!prompt.trim()) return toast.error('Enter a dashboard prompt first.')

    if (isDemoMode) {
      // Pick a close demo or generate randomized matching charts
      const match = DEMO_DASHBOARDS.find(d => d.prompt.toLowerCase().includes(prompt.toLowerCase()))
      if (match) {
        loadDemo(match)
      } else {
        // Generate a random mock matching prompt
        setDashboardTitle(prompt)
        const mockCharts: LoadedChart[] = [
          {
            spec: {
              type: 'LineChart',
              title: `Daily Trend: ${prompt}`,
              sql: "SELECT date, count FROM metrics_table",
              x_axis: "date",
              y_axis: "count",
              color: "#00E5FF",
              description: "AI-Generated trend simulation for your prompt."
            },
            data: Array.from({ length: 7 }).map((_, i) => ({ date: `05/${15 + i}`, count: Math.round(30 + Math.random() * 70) })),
            loading: false,
            error: null
          },
          {
            spec: {
              type: 'BarChart',
              title: `Segment Analysis: ${prompt}`,
              sql: "SELECT segment, value FROM segment_metrics",
              x_axis: "segment",
              y_axis: "value",
              color: "#00C896",
              description: "AI-Generated group distribution breakdown."
            },
            data: [
              { segment: "North America", value: Math.round(50 + Math.random() * 50) },
              { segment: "EMEA", value: Math.round(30 + Math.random() * 40) },
              { segment: "APAC", value: Math.round(20 + Math.random() * 30) }
            ],
            loading: false,
            error: null
          }
        ]
        setCharts(mockCharts)
        toast.success('Generated simulated demo charts')
      }
      return
    }

    // Live Database Mode
    if (!connectionId) return toast.error('No database connected.')
    setLoading(true)
    setDashboardTitle(prompt)

    try {
      const res = await api.post('/ai/dashboard', {
        user_prompt: prompt,
        connection_id: connectionId,
        role: user?.role || 'viewer',
      })

      const chartSpecs: ChartSpec[] = res.data.charts

      if (!chartSpecs || chartSpecs.length === 0) {
        toast.error('AI could not identify relevant charts for this prompt.')
        setLoading(false)
        return
      }

      // Initialize chart states with skeletons
      const initialCharts = chartSpecs.map((spec) => ({
        spec,
        data: [],
        loading: true,
        error: null
      }))
      setCharts(initialCharts)

      // Execute each query independently
      chartSpecs.forEach(async (spec, idx) => {
        try {
          const runRes = await api.post('/database/execute', {
            connection_id: connectionId,
            sql: spec.sql,
            role: user?.role || 'viewer'
          })

          setCharts((prev) => {
            const copy = [...prev]
            if (copy[idx]) {
              copy[idx] = {
                ...copy[idx],
                data: runRes.data.rows,
                loading: false,
                error: null
              }
            }
            return copy
          })
        } catch (err: any) {
          const detail = err?.response?.data?.detail || err?.message || 'Failed to fetch query data'
          setCharts((prev) => {
            const copy = [...prev]
            if (copy[idx]) {
              copy[idx] = {
                ...copy[idx],
                loading: false,
                error: typeof detail === 'string' ? detail : 'Execution safety block or table restriction.'
              }
            }
            return copy
          })
        }
      })

      toast.success(`Dashboard configured. Loading ${chartSpecs.length} query modules...`)
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || err?.message || 'Failed to generate dashboard layout')
    } finally {
      setLoading(false)
    }
  }

  function handleInspectSQL(sql: string) {
    localStorage.setItem('qs_last_sql', sql)
    window.dispatchEvent(new Event('qs_sql_update'))
    toast.success('Loaded chart query into SQL Console')
  }

  function renderChartContent(c: LoadedChart) {
    if (c.loading) {
      return (
        <div className="h-56 flex flex-col items-center justify-center space-y-3 bg-black/5 dark:bg-black/10 rounded-xl">
          <div className="flex gap-1.5">
            <span className="loading-dot bg-[var(--accent-cyan)]"></span>
            <span className="loading-dot bg-[var(--accent-cyan)]"></span>
            <span className="loading-dot bg-[var(--accent-cyan)]"></span>
          </div>
          <span className="text-[10px] text-[--text-muted] font-mono">Running query on connected DB...</span>
        </div>
      )
    }

    if (c.error) {
      return (
        <div className="h-56 flex flex-col items-center justify-center p-4 text-center bg-[var(--accent-red)]/5 border border-[var(--accent-red)]/10 rounded-xl space-y-2">
          <span className="text-xl">⚠️</span>
          <span className="text-xs font-semibold text-[var(--accent-red)]">BLOCKED / QUERY ERROR</span>
          <p className="text-[10px] text-[--text-muted] max-w-xs leading-relaxed">{c.error}</p>
        </div>
      )
    }

    if (c.data.length === 0) {
      return (
        <div className="h-56 flex items-center justify-center bg-black/5 dark:bg-black/10 rounded-xl text-xs text-[--text-muted]">
          No data returned from database execution.
        </div>
      )
    }

    const color = c.spec.color || '#00C896'
    const tickColor = isDarkTheme ? "rgba(255,255,255,0.4)" : "rgba(0,0,0,0.5)"
    const tooltipStyle = isDarkTheme 
      ? { backgroundColor: '#0c0f17', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff' }
      : { backgroundColor: '#ffffff', border: '1px solid rgba(0,0,0,0.15)', borderRadius: '8px', color: '#000' }

    switch (c.spec.type) {
      case 'BarChart':
        return (
          <ResponsiveContainer width="100%" height={230}>
            <BarChart data={c.data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <XAxis dataKey={c.spec.x_axis} stroke={tickColor} fontSize={10} tickLine={false} />
              <YAxis stroke={tickColor} fontSize={10} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey={c.spec.y_axis} fill={color} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )
      case 'AreaChart':
        return (
          <ResponsiveContainer width="100%" height={230}>
            <AreaChart data={c.data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <defs>
                <linearGradient id={`gradient-${c.spec.title}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={color} stopOpacity={0.4}/>
                  <stop offset="95%" stopColor={color} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey={c.spec.x_axis} stroke={tickColor} fontSize={10} tickLine={false} />
              <YAxis stroke={tickColor} fontSize={10} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Area type="monotone" dataKey={c.spec.y_axis} stroke={color} fillOpacity={1} fill={`url(#gradient-${c.spec.title})`} />
            </AreaChart>
          </ResponsiveContainer>
        )
      case 'PieChart':
        return (
          <ResponsiveContainer width="100%" height={230}>
            <PieChart>
              <Pie
                data={c.data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={4}
                dataKey={c.spec.y_axis}
                nameKey={c.spec.x_axis}
              >
                {c.data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={index === 0 ? color : `${color}${90 - index * 20}`} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
              <Legend verticalAlign="bottom" height={36} wrapperStyle={{ fontSize: '9px', opacity: 0.8 }} />
            </PieChart>
          </ResponsiveContainer>
        )
      case 'LineChart':
      default:
        return (
          <ResponsiveContainer width="100%" height={230}>
            <LineChart data={c.data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
              <XAxis dataKey={c.spec.x_axis} stroke={tickColor} fontSize={10} tickLine={false} />
              <YAxis stroke={tickColor} fontSize={10} tickLine={false} />
              <Tooltip contentStyle={tooltipStyle} />
              <Line type="monotone" dataKey={c.spec.y_axis} stroke={color} strokeWidth={2.5} dot={{ r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        )
    }
  }

  return (
    <div className="flex-1 p-6 space-y-6 overflow-y-auto scrollbar-thin">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[var(--border-subtle)] pb-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-[--text-primary]">Dynamic AI Dashboards</h2>
          <p className="text-xs text-[--text-muted]">
            Compile prompt-targeted chart analytics with automated read-only safety-enforced SQL streams.
          </p>
        </div>

        {/* Demo Mode / DB Connection toggle indicators */}
        <div className="flex items-center gap-2.5">
          {connectionId ? (
            <span className="text-[10px] font-bold uppercase tracking-wider bg-[var(--accent-green)]/15 text-[var(--accent-green)] border border-[var(--accent-green)]/20 px-2.5 py-1 rounded-full flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-[var(--accent-green)]"></span>
              Live Database Mode
            </span>
          ) : (
            <span className="text-[10px] font-bold uppercase tracking-wider bg-black/5 dark:bg-white/5 text-[--text-muted] border border-[var(--border-subtle)] px-2.5 py-1 rounded-full flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-[--text-muted]"></span>
              Demo Mode Active
            </span>
          )}
        </div>
      </div>

      {/* Demo Preset Selection (displayed only if no database is connected) */}
      {isDemoMode && (
        <div className="glass p-5 rounded-2xl border border-[var(--border-subtle)] space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-[--text-muted]">Select a Demo Preset</h3>
            <span className="text-[10px] text-[var(--accent-cyan)] font-medium">No DB Connected</span>
          </div>
          <div className="flex flex-wrap gap-3">
            {DEMO_DASHBOARDS.map((preset) => (
              <button
                key={preset.name}
                onClick={() => loadDemo(preset)}
                className="px-4 py-2 bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 text-xs font-medium rounded-xl border border-[var(--border-subtle)] transition-all cursor-pointer"
              >
                📊 {preset.name} Preset
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Prompt Generator Bar */}
      <form onSubmit={generateDashboard} className="flex gap-3 max-w-4xl bg-[var(--bg-surface)] p-2 rounded-2xl border border-[var(--border-subtle)] shadow-card">
        <input
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="qs-input flex-1 border-0 bg-transparent py-2.5 px-4 text-sm"
          placeholder="Describe your dashboard (e.g. 'department payroll and active clearings')..."
        />
        <button
          type="submit"
          disabled={loading || !prompt.trim()}
          className="qs-btn-primary px-6 py-2.5 text-xs font-semibold cursor-pointer shadow-glow"
        >
          {loading ? 'Analyzing Layout...' : 'Generate Dashboard'}
        </button>
      </form>

      {/* Dashboard Result Workspace */}
      {charts.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold tracking-wide text-[--text-secondary] capitalize">
              {dashboardTitle}
            </h3>
            <span className="text-[10px] text-[--text-muted] font-mono">{charts.length} charts rendered</span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {charts.map((c, i) => (
              <div key={i} className="glass p-5 rounded-2xl border border-[var(--border-subtle)] shadow-card space-y-4 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between gap-4 mb-1">
                    <h4 className="text-sm font-semibold text-[--text-primary] truncate">{c.spec.title}</h4>
                    {!c.loading && !c.error && (
                      <button
                        onClick={() => handleInspectSQL(c.spec.sql)}
                        className="text-[10px] font-mono uppercase text-[var(--accent-cyan)] border border-[var(--accent-cyan)]/20 px-2 py-0.5 rounded bg-[var(--accent-cyan)]/5 hover:bg-[var(--accent-cyan)]/15 transition-all"
                      >
                        Inspect SQL
                      </button>
                    )}
                  </div>
                  <p className="text-[10px] text-[--text-muted] leading-relaxed mb-4">{c.spec.description}</p>

                  {/* Render Chart Content */}
                  {renderChartContent(c)}
                </div>

                {/* Collapsible SQL preview */}
                {!c.loading && !c.error && (
                  <details className="text-[10px] text-[--text-muted] font-mono border-t border-[var(--border-subtle)] pt-3 group">
                    <summary className="cursor-pointer hover:text-[--text-secondary] select-none list-none flex justify-between items-center">
                      <span>👁️ View Generated Source SQL</span>
                      <span className="group-open:rotate-180 transition-transform">▼</span>
                    </summary>
                    <pre className="mt-2 p-2 bg-black/5 dark:bg-black/35 rounded-lg border border-[var(--border-subtle)] overflow-x-auto text-[9px] text-[var(--accent-cyan)] font-mono whitespace-pre">
                      {c.spec.sql}
                    </pre>
                  </details>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
