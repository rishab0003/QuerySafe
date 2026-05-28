"use client"

import React from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight, Database, Moon, Sun, Terminal, Zap } from 'lucide-react'
import AttackDemo from '../components/landing/AttackDemo'
import FeatureGrid from '../components/landing/FeatureGrid'
import Pipeline from '../components/landing/Pipeline'
import LogosMarquee from '../components/landing/LogosMarquee'
import Footer from '../components/Footer'

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.12, duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] },
  }),
}

function ThemeToggle({ isDark, onToggle }: { isDark: boolean; onToggle: () => void }) {
  return (
    <button onClick={onToggle} aria-label="Toggle theme" className="qs-btn-icon">
      {isDark ? <Sun size={16} /> : <Moon size={16} />}
    </button>
  )
}

export default function Home() {
  const [isDark, setIsDark] = React.useState(true)

  React.useEffect(() => {
    try {
      const savedTheme = localStorage.getItem('theme')
      const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      const shouldUseDark = savedTheme ? savedTheme === 'dark' : prefersDark

      setIsDark(shouldUseDark)
      document.documentElement.classList.toggle('dark', shouldUseDark)
      localStorage.setItem('theme', shouldUseDark ? 'dark' : 'light')
    } catch {
      setIsDark(false)
    }
  }, [])

  const toggleTheme = () => {
    try {
      const next = !isDark
      setIsDark(next)
      document.documentElement.classList.toggle('dark', next)
      localStorage.setItem('theme', next ? 'dark' : 'light')
    } catch {
      setIsDark((value) => !value)
    }
  }

  return (
    <div className="relative min-h-screen overflow-x-clip bg-[var(--bg-void)] text-[var(--text-primary)]">
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-jade/[0.06] blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-purple/[0.06] blur-[100px]" />
        <div className="absolute top-[40%] right-[20%] w-[300px] h-[300px] rounded-full bg-blue/[0.04] blur-[80px]" />
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.06) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.06) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px',
          }}
        />
      </div>

      <header className="fixed top-0 left-0 right-0 z-50 px-6 pt-4">
        <div className="glass-elevated mx-auto flex max-w-6xl items-center justify-between gap-4 rounded-2xl px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-jade to-jade-dim shadow-jade-glow">
              <Database size={16} className="text-black" />
            </div>
            <div>
              <div className="font-display text-lg font-bold tracking-tight">QuerySafe</div>
              <div className="text-xs text-[var(--text-muted)]">AI-powered database security</div>
            </div>
          </div>

          <nav className="flex items-center gap-2 sm:gap-3">
            <ThemeToggle isDark={isDark} onToggle={toggleTheme} />
            <Link href="/auth/login" className="qs-btn-ghost text-sm">
              Sign In
            </Link>
            <Link href="/dashboard" className="qs-btn-primary text-sm">
              Launch App
              <ArrowRight size={14} />
            </Link>
          </nav>
        </div>
      </header>

      <main className="relative z-10 pt-28 sm:pt-32">
        <section className="px-6 pb-20 sm:pb-24">
          <div className="mx-auto grid max-w-6xl items-center gap-12 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,0.95fr)] lg:gap-16">
            <motion.div className="max-w-2xl" initial="hidden" animate="visible">
              <motion.div custom={0} variants={fadeUp} className="mb-6 inline-flex">
                <span className="inline-flex items-center gap-2 rounded-full border border-jade/20 bg-jade/[0.10] px-4 py-1.5 text-xs font-medium text-jade">
                  <Zap size={12} />
                  AI-Powered Database Security
                </span>
              </motion.div>

              <motion.h1
                custom={1}
                variants={fadeUp}
                className="font-display text-5xl font-extrabold tracking-tight leading-[1.02] text-[var(--text-primary)] sm:text-6xl xl:text-7xl"
              >
                Query your database
                <br />
                <span
                  className="bg-gradient-to-r from-jade via-emerald-400 to-jade bg-clip-text text-transparent animate-gradient-flow"
                  style={{ backgroundSize: '200% auto' }}
                >
                  in plain English
                </span>
              </motion.h1>

              <motion.p
                custom={2}
                variants={fadeUp}
                className="mt-6 max-w-xl text-lg leading-relaxed text-[var(--text-muted)] sm:text-xl"
              >
                Natural language to SQL with enterprise-grade security. Role-based access control,
                query validation, and AI-powered dashboards.
              </motion.p>

              <motion.div custom={3} variants={fadeUp} className="mt-8 flex flex-wrap items-center gap-4">
                <Link href="/dashboard" className="qs-btn-primary rounded-xl px-7 py-3 text-base">
                  <Terminal size={16} />
                  Start Querying
                </Link>
                <Link href="/auth/register" className="qs-btn-ghost rounded-xl px-7 py-3 text-base">
                  Create Account
                </Link>
              </motion.div>
            </motion.div>

            <motion.div custom={4} variants={fadeUp} className="mx-auto w-full max-w-xl animate-float">
              <div className="glass-elevated overflow-hidden rounded-3xl shadow-elevated transition-all duration-300 hover:shadow-jade-glow">
                <div className="flex items-center gap-2 border-b border-[var(--glass-border)] px-5 py-3">
                  <div className="flex gap-1.5">
                    <div className="h-3 w-3 rounded-full bg-crimson/70" />
                    <div className="h-3 w-3 rounded-full bg-amber/70" />
                    <div className="h-3 w-3 rounded-full bg-jade/70" />
                  </div>
                  <span className="ml-2 font-mono text-[11px] text-[var(--text-muted)]">querysafe — ai terminal</span>
                </div>

                <div className="space-y-4 p-5 font-mono text-sm">
                  <div className="flex gap-2">
                    <span className="text-jade">❯</span>
                    <span className="text-[var(--text-primary)]">&quot;Show me the top 10 customers by revenue this quarter&quot;</span>
                  </div>

                  <div className="text-xs text-[var(--text-muted)]">⏳ Generating SQL...</div>

                  <div className="sql-block !mt-2 text-xs">
                    <span className="keyword">SELECT</span> c.name, <span className="function">SUM</span>(o.total){' '}
                    <span className="keyword">AS</span> revenue
                    <br />
                    <span className="keyword">FROM</span> customers c
                    <br />
                    <span className="keyword">JOIN</span> orders o <span className="keyword">ON</span> c.id = o.customer_id
                    <br />
                    <span className="keyword">WHERE</span> o.created_at {'>'}= <span className="string">&apos;2026-01-01&apos;</span>
                    <br />
                    <span className="keyword">GROUP BY</span> c.name
                    <br />
                    <span className="keyword">ORDER BY</span> revenue <span className="keyword">DESC</span>
                    <br />
                    <span className="keyword">LIMIT</span> <span className="number">10</span>
                  </div>

                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-jade">✓</span>
                    <span className="text-[var(--text-muted)]">10 rows returned in 42ms · Confidence: 96%</span>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        <FeatureGrid />
        <Pipeline />

        <motion.section 
          className="px-6 py-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
        >
          <div className="mx-auto flex max-w-6xl justify-center">
            <AttackDemo />
          </div>
        </motion.section>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
        >
          <LogosMarquee />
        </motion.div>
      </main>

      <Footer />
    </div>
  )
}