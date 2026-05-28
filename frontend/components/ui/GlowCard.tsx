import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface GlowCardProps {
  children: React.ReactNode
  className?: string
  glowColor?: 'violet' | 'indigo' | 'cyan'
}

export default function GlowCard({ children, className, glowColor = 'violet' }: GlowCardProps) {
  const glowClass = {
    violet: 'from-violet-500/10 via-purple-500/5 to-cyan-400/5',
    indigo: 'from-indigo-500/10 via-purple-500/5 to-cyan-400/5',
    cyan:   'from-cyan-500/10 via-purple-500/5 to-violet-500/5',
  }[glowColor]

  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.02 }}
      transition={{ duration: 0.2 }}
      className={cn(
        'relative rounded-2xl border border-white/10 bg-white/[0.03] backdrop-blur-sm p-6',
        'hover:border-violet-500/40 hover:shadow-glow-sm',
        className
      )}
    >
      {/* Inner gradient glow */}
      <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${glowClass} opacity-0 group-hover:opacity-100 transition-opacity`} />
      {children}
    </motion.div>
  )
}
