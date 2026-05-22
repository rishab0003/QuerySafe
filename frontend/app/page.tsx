"use client"
import React from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Database, Shield, Zap, ArrowRight, Terminal, Lock, BarChart3 } from 'lucide-react'
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

const features = [
  {
    icon: Terminal,
    title: 'Natural Language Queries',
    desc: 'Ask questions in plain English — our AI converts them to safe, optimized SQL.',
    color: '#00C896',
  },
  {
    icon: Shield,
    title: 'Enterprise Security',
    desc: 'Role-based access control, SQL injection prevention, and query validation.',
    color: '#8B5CF6',
  },
  {
    icon: BarChart3,
    title: 'Auto Dashboards',
    desc: 'Generate interactive Recharts visualizations from natural language descriptions.',
    color: '#3B82F6',
  },
  {
    icon: Lock,
    title: '2FA Authentication',
    desc: 'TOTP-based two-factor authentication with QR code setup for your team.',
    color: '#F5A623',
  },
]

export default function Home() {
  return (
    <div className="relative min-h-screen overflow-y-auto">
      {/* ─── Background Effects ─── */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-jade/[0.04] blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[500px] h-[500px] rounded-full bg-purple/[0.04] blur-[100px]" />
        <div className="absolute top-[40%] right-[20%] w-[300px] h-[300px] rounded-full bg-blue/[0.03] blur-[80px]" />
        {/* Grid overlay */}
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage: `
              linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
              linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)
            `,
            backgroundSize: '60px 60px',
          }}
        />
      </div>

      {/* ─── Navbar ─── */}
      <header className="fixed top-0 left-0 right-0 z-50">
        <div className="glass-elevated mx-4 mt-4 rounded-2xl px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-jade to-jade-dim flex items-center justify-center shadow-jade-glow">
              <Database size={16} className="text-black" />
            </div>
            <span className="font-display text-lg font-bold tracking-tight">QuerySafe</span>
          </div>
          <nav className="flex items-center gap-2">
            <Link
              href="/auth/login"
              className="qs-btn-ghost text-sm"
            >
              Sign In
            </Link>
            <Link
              href="/dashboard"
              className="qs-btn-primary text-sm"
            >
              Launch App
              <ArrowRight size={14} />
            </Link>
          </nav>
        </div>
      </header>

      {/* ─── Hero ─── */}
      <section className="relative flex flex-col items-center justify-center min-h-screen px-6 pt-24 pb-16">
        <motion.div
          className="text-center max-w-3xl"
          initial="hidden"
          animate="visible"
        >
          {/* Badge */}
          <motion.div custom={0} variants={fadeUp} className="mb-6 inline-flex">
            <span className="inline-flex items-center gap-2 rounded-full bg-jade/[0.08] border border-jade/20 px-4 py-1.5 text-xs font-medium text-jade">
              <Zap size={12} />
              AI-Powered Database Security
            </span>
          </motion.div>

          {/* Heading */}
          <motion.h1
            custom={1}
            variants={fadeUp}
            className="font-display text-5xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight leading-[1.08] mb-5"
          >
            Query your database
            <br />
            <span className="bg-gradient-to-r from-jade via-emerald-400 to-jade bg-clip-text text-transparent animate-gradient-flow" style={{ backgroundSize: '200% auto' }}>
              in plain English
            </span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            custom={2}
            variants={fadeUp}
            className="text-ink-300 text-lg sm:text-xl max-w-xl mx-auto leading-relaxed mb-10"
          >
            Natural language to SQL with enterprise-grade security.
            Role-based access control, query validation, and AI-powered dashboards.
          </motion.p>

          {/* CTAs */}
          <motion.div custom={3} variants={fadeUp} className="flex items-center justify-center gap-4">
            <Link href="/dashboard" className="qs-btn-primary px-7 py-3 text-base rounded-xl">
              <Terminal size={16} />
              Start Querying
            </Link>
            <Link href="/auth/register" className="qs-btn-ghost px-7 py-3 text-base rounded-xl">
              Create Account
            </Link>
          </motion.div>

          {/* Terminal Preview */}
          <motion.div
            custom={4}
            variants={fadeUp}
            className="mt-14 max-w-2xl mx-auto"
          >
            <div className="glass-elevated rounded-2xl overflow-hidden">
              {/* Title bar */}
              <div className="flex items-center gap-2 px-5 py-3 border-b border-white/[0.04]">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-crimson/60" />
                  <div className="w-3 h-3 rounded-full bg-amber/60" />
                  <div className="w-3 h-3 rounded-full bg-jade/60" />
                </div>
                <span className="text-[11px] text-ink-500 ml-2 font-mono">querysafe — ai terminal</span>
              </div>
              {/* Content */}
              <div className="p-5 font-mono text-sm space-y-3">
                <div className="flex gap-2">
                  <span className="text-jade">❯</span>
                  <span className="text-ink-200">&quot;Show me the top 10 customers by revenue this quarter&quot;</span>
                </div>
                <div className="text-ink-500 text-xs">⏳ Generating SQL...</div>
                <div className="sql-block !mt-2 text-xs">
                  <span className="keyword">SELECT</span> c.name, <span className="function">SUM</span>(o.total) <span className="keyword">AS</span> revenue
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
                  <span className="text-ink-400">10 rows returned in 42ms · Confidence: 96%</span>
                </div>
              </div>
            </div>
          </motion.div>
        <FeatureGrid />
        <Pipeline />
        <section className="py-12 px-6 flex justify-center">
          <AttackDemo />
        </section>
        <LogosMarquee />
        <Footer />
        </motion.div>
      </section>

      {/* ─── Features Grid ─── */}
      <section className="relative px-6 pb-24">
        <motion.div
          className="max-w-5xl mx-auto grid grid-cols-1 sm:grid-cols-2 gap-5"
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
        >
          {features.map((f, i) => (
            <motion.div
              key={f.title}
              custom={i}
              variants={fadeUp}
              className="glass-elevated rounded-2xl p-6 group hover:border-white/[0.12] transition-all duration-300"
            >
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center mb-4"
                style={{ background: `${f.color}12`, border: `1px solid ${f.color}25` }}
              >
                <f.icon size={18} style={{ color: f.color }} />
              </div>
              <h3 className="text-base font-semibold mb-2 text-white group-hover:text-jade transition-colors duration-300">
                {f.title}
              </h3>
              <p className="text-sm text-ink-400 leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </section>

      {/* ─── Footer ─── */}
      <footer className="relative border-t border-white/[0.04] py-8 px-6">
        <div className="max-w-5xl mx-auto flex items-center justify-between text-xs text-ink-500">
          <span>© 2026 QuerySafe. Enterprise-grade AI database security.</span>
          <div className="flex items-center gap-1">
            <div className="status-dot online" />
            <span className="ml-1">All systems operational</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
