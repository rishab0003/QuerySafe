import React, { useEffect, useRef } from 'react'
import { cn } from '@/lib/utils'

/**
 * ParticleField – a lightweight CSS‑based particle animation.
 * Renders a set of small circles that float in the background with a subtle glow.
 * The component is fully configurable via CSS variables; the defaults match the
 * design system (purple‑cyan gradient). It is used in the final CTA section.
 */
interface ParticleFieldProps {
  /** Number of particles to render (default: 30) */
  count?: number
  /** CSS class for custom sizing / positioning */
  className?: string
}

export default function ParticleField({ count = 30, className }: ParticleFieldProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  // Generate an array of particle positions & animation delays
  const particles = Array.from({ length: count }, (_, i) => {
    const size = Math.random() * 3 + 2 // 2‑5px
    const left = Math.random() * 100 // percent
    const delay = Math.random() * 5 // seconds
    const duration = Math.random() * 4 + 6 // 6‑10s
    return { size, left, delay, duration, key: i }
  })

  useEffect(() => {
    // Cleanup on unmount (no timers needed – pure CSS animation)
    return () => {}
  }, [])

  return (
    <div
      ref={containerRef}
      className={cn('absolute inset-0 pointer-events-none overflow-hidden', className)}
    >
      {particles.map(p => (
        <div
          key={p.key}
          className="particle"
          style={{
            width: `${p.size}px`,
            height: `${p.size}px`,
            left: `${p.left}%`,
            animationDelay: `${p.delay}s`,
            animationDuration: `${p.duration}s`,
          }}
        />
      ))}
      <style jsx>{`
        .particle {
          position: absolute;
          bottom: -10px;
          background: radial-gradient(circle, rgba(124,58,237,0.6), transparent);
          border-radius: 50%;
          opacity: 0.3;
          animation-name: rise;
          animation-timing-function: ease-in-out;
          animation-iteration-count: infinite;
        }
        @keyframes rise {
          0% { transform: translateY(0) scale(1); opacity: 0.3; }
          50% { opacity: 0.6; }
          100% { transform: translateY(-120vh) scale(0.5); opacity: 0; }
        }
      `}</style>
    </div>
  )
}
