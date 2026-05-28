import React from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

type Variant = 'primary' | 'outline' | 'ghost'

interface GlowButtonProps extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'onAnimationStart' | 'onDrag' | 'onDragStart' | 'onDragEnd'> {
  variant?: Variant
  children: React.ReactNode
  className?: string
}

export default function GlowButton({ variant = 'primary', children, className, ...rest }: GlowButtonProps) {
  const base = 'px-6 py-3 rounded-xl font-body font-medium text-sm transition-all duration-200 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-cyan)]'
  const variants: Record<Variant, string> = {
    primary: `bg-gradient-to-r from-violet-600 to-indigo-600 dark:from-violet-500 dark:to-indigo-500 text-white hover:shadow-glow-md hover:scale-[1.02] active:scale-[0.98]`,
    outline: `border border-[var(--border-subtle)] text-[--text-muted] hover:border-[var(--accent-cyan)]/50 hover:text-[--text-primary] hover:bg-black/5 dark:hover:bg-white/5`,
    ghost: `text-[--text-muted] hover:text-[--text-primary] hover:bg-black/5 dark:hover:bg-white/5`
  }

  return (
    <motion.button
      whileTap={{ scale: 0.97 }}
      className={cn(base, variants[variant], className)}
      {...rest}
    >
      {children}
    </motion.button>
  )
}
