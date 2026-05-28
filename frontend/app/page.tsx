"use client"

import React from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight, Database, Moon, Sun, Terminal, Zap } from 'lucide-react'
import AttackDemo from '../components/landing/AttackDemo'
import FeaturesGrid from '@/components/sections/FeaturesGrid'
import AnalyticsShowcase from '@/components/sections/AnalyticsShowcase'
import NotebookSection from '@/components/sections/NotebookSection'
import MetricsSection from '@/components/sections/MetricsSection'
import IntegrationsSection from '@/components/sections/IntegrationsSection'
import TestimonialsSection from '@/components/sections/TestimonialsSection'
import PricingSection from '@/components/sections/PricingSection'
import FinalCTA from '@/components/sections/FinalCTA'
import LogosMarquee from '../components/landing/LogosMarquee'
import Footer from '../components/Footer'
import { useTheme } from '@/hooks/useTheme'
import PremiumHero from '@/components/sections/PremiumHero'

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.12, duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] },
  }),
}



export default function Home() {
  const { theme, toggle } = useTheme();
  const isDark = theme === 'dark';

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
            <button onClick={toggle} aria-label="Toggle theme" className="qs-btn-icon">
              {isDark ? <Sun size={16} /> : <Moon size={16} />}
            </button>
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
        <PremiumHero />

        <FeaturesGrid />
        <AnalyticsShowcase />
        <NotebookSection />
        <MetricsSection />
        <IntegrationsSection />
        <TestimonialsSection />
        <PricingSection />
        <FinalCTA />
      </main>

      <Footer />
    </div>
  )
}