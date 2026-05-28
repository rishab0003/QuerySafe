"use client"
import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

const nodes = [
  { id: 'prompt', label: 'User Prompt', color: '#0b9ec2' },
  { id: 'auth', label: '2FA Auth', color: '#c47a00' },
  { id: 'rbac', label: 'RBAC Check', color: '#0a9d68' },
  { id: 'ai', label: 'AI Engine', color: '#0b9ec2' },
  { id: 'validator', label: 'SQL Validator', color: '#0a9d68' },
  { id: 'db', label: 'Read-Only DB', color: '#7c5ce6' },
  { id: 'audit', label: 'Audit Log', color: '#5d6877' },
]

export default function Pipeline() {
  const [activeIndex, setActiveIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % nodes.length)
    }, 1600)
    return () => clearInterval(interval)
  }, [])

  return (
    <section className="px-6 pb-12">
      <div className="mx-auto max-w-6xl">
        <h3 className="text-lg font-medium mb-4 text-[var(--text-primary)]">AI Security Pipeline</h3>
        <motion.div 
          className="glass overflow-hidden rounded-2xl p-6"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 relative py-2">
            {nodes.map((n, i) => {
              const isActive = i === activeIndex
              return (
                <React.Fragment key={n.id}>
                  <motion.div
                    className={`flex items-center justify-center rounded-xl px-5 py-3 border text-sm font-medium transition-all duration-300 flex-1 text-center min-h-[48px] ${
                      isActive 
                        ? 'border-transparent text-white font-bold' 
                        : 'border-[var(--border-subtle)] text-[var(--text-muted)] bg-[var(--bg-surface)]'
                    }`}
                    style={{
                      background: isActive 
                        ? `linear-gradient(135deg, ${n.color}, var(--jade-dim))`
                        : 'var(--bg-surface)',
                      boxShadow: isActive ? `0 8px 24px ${n.color}35` : 'none',
                    }}
                    animate={isActive ? { scale: 1.05 } : { scale: 1 }}
                    transition={{ type: "spring", stiffness: 200, damping: 12 }}
                  >
                    <span className="relative z-10">{n.label}</span>
                  </motion.div>
                  
                  {i < nodes.length - 1 && (
                    <div className="flex md:flex-col items-center justify-center h-4 w-full md:h-px md:w-8 shrink-0 relative">
                      <div className="h-1 md:h-0.5 w-0.5 md:w-full bg-[var(--border-subtle)] relative overflow-hidden flex-1">
                        {isActive && (
                          <motion.div
                            className="absolute top-0 left-0 h-full w-full rounded-full"
                            style={{ backgroundColor: n.color }}
                            initial={{ scaleX: 0, transformOrigin: "left" }}
                            animate={{ scaleX: 1 }}
                            transition={{ duration: 1.6, ease: "easeInOut" }}
                          />
                        )}
                      </div>
                    </div>
                  )}
                </React.Fragment>
              )
            })}
          </div>
        </motion.div>
      </div>
    </section>
  )
}
