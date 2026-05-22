"use client"
import React from 'react'

export default function AnimatedBackground(){
  return (
    <div className="w-full h-56 mb-6 rounded overflow-hidden relative shadow-jade-glow">
      <div className="absolute inset-0 bg-gradient-to-r from-ink-800/80 via-ink-700/60 to-ink-800/80" />
      <div className="relative p-6 flex items-center h-full">
        <div className="w-full">
          <h3 className="text-2xl font-display font-semibold">Security pipeline</h3>
          <p className="text-ink-400 mt-2">AI pipeline visualization — interactive in the full implementation.</p>
        </div>
      </div>
      <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_bottom_right,_rgba(0,200,150,0.06),transparent_20%)]" />
    </div>
  )
}
