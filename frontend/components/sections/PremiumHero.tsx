import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Database, Moon, Sun, Terminal, Zap } from 'lucide-react';
import { fadeUp, stagger } from '@/lib/motion';
import { useTheme } from '@/hooks/useTheme';

export default function PremiumHero() {
  const { theme, toggle } = useTheme();
  const isDark = theme === 'dark';

  return (
    <section className="relative min-h-screen flex items-center justify-center bg-gradient-to-b from-[var(--bg-surface)] to-[var(--bg-void)] overflow-hidden">
      {/* Animated glowing blobs */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-[-30%] left-[-10%] w-[500px] h-[500px] rounded-full bg-jade/[0.07] blur-[120px] animate-glow-pulse" />
        <div className="absolute bottom-[-30%] right-[-10%] w-[500px] h-[500px] rounded-full bg-purple/[0.07] blur-[120px] animate-glow-pulse" />
      </div>

      <motion.div
        variants={stagger}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: '-80px' }}
        className="text-center max-w-2xl z-10 px-4"
      >
        {/* Badge */}
        <motion.div variants={fadeUp} className="inline-block px-4 py-1 mb-4 bg-black/5 dark:bg-white/5 border border-[var(--border-subtle)] rounded-full text-xs text-[--text-muted]">
          🔒 Read‑Only Enforced • AES‑256 Encrypted
        </motion.div>

        {/* Headline */}
        <motion.h1 variants={fadeUp} className="text-5xl sm:text-6xl lg:text-7xl font-display font-bold text-[--text-primary] mb-6">
          Query your database
          <br />
          <span className="bg-gradient-to-r from-jade via-emerald-400 to-jade bg-clip-text text-transparent animate-gradient-flow" style={{ backgroundSize: '200% auto' }}>
            in plain English
          </span>
        </motion.h1>

        {/* Sub‑headline */}
        <motion.p variants={fadeUp} className="text-lg text-[--text-muted] mb-8">
          AI‑powered natural language to SQL with role‑based read‑only access, zero‑code analytics, and enterprise security.
        </motion.p>

        {/* CTA Buttons */}
        <motion.div variants={fadeUp} className="flex gap-4 justify-center items-center">
          <Link href="/dashboard" className="qs-btn-primary rounded-xl px-7 py-3 text-base flex items-center gap-2">
            <Terminal size={16} />
            Start Querying
          </Link>
          <Link href="/auth/register" className="qs-btn-ghost rounded-xl px-7 py-3 text-base border border-[var(--border-subtle)] hover:bg-black/5 dark:hover:bg-white/5">
            Create Account
          </Link>
          <button onClick={toggle} aria-label="Toggle theme" className="qs-btn-icon p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/5 transition-colors">
            {isDark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </motion.div>
      </motion.div>
    </section>
  );
}
