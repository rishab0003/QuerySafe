import React from 'react'
import SectionWrapper from '@/components/ui/SectionWrapper'
import GradientText from '@/components/ui/GradientText'
import GlowCard from '@/components/ui/GlowCard'
import { motion } from 'framer-motion'
import { fadeUp, stagger } from '@/lib/motion'

export default function AnalyticsShowcase() {
  return (
    <SectionWrapper id="analytics" className="bg-surface-base">
      <motion.div variants={stagger} initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-80px' }}>
        <motion.h2 variants={fadeUp} className="text-4xl font-display font-bold text-center mb-8 text-white">
          Instant AI Analytics
        </motion.h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <GlowCard>
            <h3 className="font-display text-lg font-semibold mb-2 text-white">Ask a Question</h3>
            <p className="text-zinc-300">"Show me the top 10 customers by revenue this quarter"</p>
          </GlowCard>
          <GlowCard>
            <h3 className="font-display text-lg font-semibold mb-2 text-white">Live Results</h3>
            <p className="text-zinc-300">SQL generated instantly, results visualized in a chart.</p>
          </GlowCard>
        </div>
      </motion.div>
    </SectionWrapper>
  )
}
