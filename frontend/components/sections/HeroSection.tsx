import React from 'react'
import { motion } from 'framer-motion'
import GradientText from '@/components/ui/GradientText'
import GlowButton from '@/components/ui/GlowButton'
import { fadeUp, stagger } from '@/lib/motion'
import { useTheme } from '@/hooks/useTheme'

export default function HeroSection() {
  const { theme, toggle } = useTheme()

  return (
    <section className="relative min-h-screen flex items-center justify-center bg-grid bg-noise overflow-hidden">
      {/* Background glow orb */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-[-20%] left-1/2 w-[600px] h-[600px] -translate-x-1/2 bg-gradient-to-r from-violet-600 to-cyan-400 opacity-30 rounded-full animate-glow-pulse" />
      </div>

      <motion.div
        variants={stagger}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: '-80px' }}
        className="text-center max-w-2xl z-10"
      >
        {/* Badge */}
        <motion.div
          variants={fadeUp}
          className="inline-block px-4 py-1 mb-4 bg-white/5 border border-white/10 rounded-full text-xs text-zinc-300"
        >
          🔒 Read‑Only Enforced • AES‑256 Encrypted
        </motion.div>

        {/* Headline */}
        <motion.h1 variants={fadeUp} className="text-5xl sm:text-6xl lg:text-7xl font-display font-bold text-white mb-6">
          Ask Your Database <GradientText>Securely.</GradientText>
        </motion.h1>

        {/* Sub‑headline */}
        <motion.p variants={fadeUp} className="text-lg text-zinc-300 mb-8">
          Natural‑language AI queries with role‑based read‑only access. No SQL needed.
        </motion.p>

        {/* CTA buttons */}
        <motion.div variants={fadeUp} className="flex gap-4 justify-center items-center">
          <GlowButton variant="primary" onClick={() => {/* navigate to signup */}}>
            Get Started Free
          </GlowButton>
          <GlowButton variant="outline" onClick={() => {/* navigate to demo */}}>
            Book a Demo
          </GlowButton>
          {/* Theme toggle */}
          <button
            onClick={toggle}
            aria-label="Toggle theme"
            className="p-2 rounded-full hover:bg-white/5 transition-colors"
          >
            {theme === 'dark' ? (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor"><path d="M10 2a1 1 0 011 1v2a1 1 0 11-2 0V3a1 1 0 011-1zm4.22 2.2a1 1 0 011.42 0l1.42 1.42a1 1 0 01-1.42 1.42L14.64 5.6a1 1 0 010-1.4zM18 9a1 1 0 110 2h-2a1 1 0 110-2h2zM14.22 14.78a1 1 0 010 1.42l-1.42 1.42a1 1 0 01-1.42-1.42l1.42-1.42a1 1 0 011.42 0zM10 14a1 1 0 011 1v2a1 1 0 11-2 0v-2a1 1 0 011-1zm-4.22-2.2a1 1 0 00-1.42 0L2.94 13.22a1 1 0 101.42 1.42l1.42-1.42a1 1 0 000-1.42zM4 9a1 1 0 100 2H2a1 1 0 100-2h2zM5.36 5.6a1 1 0 010 1.4L3.94 8.42a1 1 0 01-1.42-1.42L3.94 5.6a1 1 0 011.42 0z"/></svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor"><path d="M10 2a8 8 0 100 16 8 8 0 000-16z"/></svg>
            )}
          </button>
        </motion.div>
      </motion.div>
    </section>
  )
}
