import React from 'react'
import SectionWrapper from '@/components/ui/SectionWrapper'
import GlowCard from '@/components/ui/GlowCard'
import { motion } from 'framer-motion'
import { fadeUp, stagger } from '@/lib/motion'

export default function NotebookSection() {
  return (
    <SectionWrapper id="notebook" className="bg-surface-base">
      <motion.div variants={stagger} initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-80px' }}>
        <motion.h2 variants={fadeUp} className="text-4xl font-display font-bold text-center mb-8 text-white">
          Interactive Notebook
        </motion.h2>
        <div className="flex flex-col items-center gap-6">
          <GlowCard className="max-w-3xl w-full p-6">
            <p className="text-zinc-300">Compose queries in a Jupyter‑style notebook and watch AI generate results instantly.</p>
          </GlowCard>
        </div>
      </motion.div>
    </SectionWrapper>
  )
}
