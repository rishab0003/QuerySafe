import React from 'react'
import SectionWrapper from '@/components/ui/SectionWrapper'
import GlowCard from '@/components/ui/GlowCard'
import { motion } from 'framer-motion'
import { fadeUp, stagger } from '@/lib/motion'
import { useAnimatedCounter } from '@/hooks/useAnimatedCounter'
import { TrendingUp, BarChart2, Database, Users } from 'lucide-react'

export default function MetricsSection() {
  const queries = useAnimatedCounter(12457)
  const users = useAnimatedCounter(842)
  const dbs = useAnimatedCounter(12)
  const dashboards = useAnimatedCounter(38)

  const stats = [
    { icon: Users, label: 'Active Users', value: users },
    { icon: Database, label: 'Databases Secured', value: dbs },
    { icon: BarChart2, label: 'Dashboards Created', value: dashboards },
    { icon: TrendingUp, label: 'Queries Run', value: queries },
  ]

  return (
    <SectionWrapper id="metrics" className="bg-surface-base">
      <motion.div variants={stagger} initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-80px' }}>
        <motion.h2 variants={fadeUp} className="text-4xl font-display font-bold text-center mb-8 text-[--text-primary]">
          Powerful Metrics
        </motion.h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((s, i) => (
            <GlowCard key={i} className="flex flex-col items-center p-4 text-center">
              <s.icon className="h-8 w-8 mb-2 text-[--text-primary]" />
              <p className="text-sm text-[--text-muted] mb-1">{s.label}</p>
              <p className="text-2xl font-bold text-[--text-primary]">
                <motion.span ref={s.value.ref}>{s.value.display}</motion.span>
              </p>
            </GlowCard>
          ))}
        </div>
      </motion.div>
    </SectionWrapper>
  )
}
