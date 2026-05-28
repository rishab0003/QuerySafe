import React from 'react'

interface MarqueeProps {
  children: React.ReactNode
  className?: string
  pauseOnHover?: boolean
}

export default function Marquee({ children, className = '', pauseOnHover = false }: MarqueeProps) {
  return (
    <div className={`marquee ${className}`}>
      <div className={`marquee-track ${pauseOnHover ? 'hover:[animation-play-state:paused]' : ''}`}>
        {children}
        {children}
      </div>
    </div>
  )
}
