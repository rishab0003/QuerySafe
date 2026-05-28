import React from 'react'
import { cn } from '@/lib/utils'

interface GradientTextProps {
  children: React.ReactNode
  className?: string
}

export function GradientText({ children, className }: GradientTextProps) {
  return (
    <span
      className={cn(
        'bg-gradient-to-r from-violet-400 via-purple-400 to-cyan-400 bg-clip-text text-transparent',
        className
      )}
    >
      {children}
    </span>
  )
}

export default GradientText
