import React from 'react'
import GlowCard from '@/components/ui/GlowCard'
import GradientText from '@/components/ui/GradientText'
import SectionWrapper from '@/components/ui/SectionWrapper'
import { motion } from 'framer-motion'
import { fadeUp, stagger } from '@/lib/motion'
import { Lock, Brain, Shield, Users, Key, Eye, Database, BarChart2 } from 'lucide-react'

const features = [
  {
    icon: Lock,
    title: 'Read‑Only Enforced',
    description: 'Triple‑layer enforcement: prompt, SQL validator, and DB driver. SELECT only. Always.',
    gradient: 'from-violet-500 to-purple-600',
  },
  {
    icon: Brain,
    title: 'AI Query Engine',
    description: 'Natural language to SQL via Claude/GPT‑4 with schema‑aware context and confidence scoring.',
    gradient: 'from-indigo-500 to-blue-600',
  },
  {
    icon: Shield,
    title: 'AES‑256 Encryption',
    description: 'All database credentials encrypted at rest. Zero plaintext storage.',
    gradient: 'from-emerald-500 to-teal-600',
  },
  {
    icon: Users,
    title: 'Role‑Based Access',
    description: 'HR sees HR data. Finance sees Finance data. Zero cross‑department leakage.',
    gradient: 'from-orange-500 to-amber-600',
  },
  {
    icon: Key,
    title: 'Two‑Factor Auth',
    description: 'TOTP + Google SSO. JWT tokens with refresh rotation.',
    gradient: 'from-pink-500 to-rose-600',
  },
  {
    icon: Eye,
    title: 'AI Explainability',
    description: 'See the exact SQL, tables used, and confidence score for every query.',
    gradient: 'from-cyan-500 to-sky-600',
  },
  {
    icon: Database,
    title: 'Multi‑DB Support',
    description: 'PostgreSQL, MySQL, MongoDB, Snowflake, BigQuery, SQL Server.',
    gradient: 'from-violet-500 to-indigo-600',
  },
  {
    icon: BarChart2,
    title: 'Auto Dashboards',
    description: '“Create a monthly sales dashboard” — charts appear instantly.',
    gradient: 'from-purple-500 to-fuchsia-600',
  },
]

export default function FeaturesGrid() {
  return (
    <SectionWrapper id="features" className="bg-surface-base">
      <motion.div variants={stagger} initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-80px' }}>
        <motion.h2 variants={fadeUp} className="text-4xl font-display font-bold text-center mb-8 text-white">
          Why QuerySafe?
        </motion.h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((f, i) => (
            <GlowCard key={i} className="group hover:border-violet-500/40">
              <div className="flex items-center gap-3 mb-3">
                <f.icon className={`h-6 w-6 text-white bg-gradient-to-r ${f.gradient} bg-clip-text text-transparent`} />
                <h3 className="font-display text-lg font-semibold text-white">{f.title}</h3>
              </div>
              <p className="text-zinc-300 text-sm">{f.description}</p>
            </GlowCard>
          ))}
        </div>
      </motion.div>
    </SectionWrapper>
  )
}
