"use client"
import React from 'react'
import { motion } from 'framer-motion'
import { Lock, Cpu, Shield, Users, Key, BarChart3 } from 'lucide-react'

const items = [
  { title: 'Read-Only Enforcement', icon: Lock, desc: 'Strictly enforces non-destructive queries.' },
  { title: 'AI-Powered Queries', icon: Cpu, desc: 'Natural language -> safe SQL generation.' },
  { title: 'SQL Safety Engine', icon: Shield, desc: 'Runtime validation and blocking.' },
  { title: 'Role-Based Access', icon: Users, desc: 'Fine-grained RBAC filters per dept.' },
  { title: 'AES-256 Encryption', icon: Key, desc: 'Encrypted credentials & secrets.' },
  { title: 'Auto Dashboards', icon: BarChart3, desc: 'Generate visualizations from prompts.' },
]

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
    },
  },
}

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      type: "spring",
      stiffness: 90,
      damping: 14,
    },
  },
}

export default function FeatureGrid(){
  return (
    <section className="px-6 pb-24">
      <div className="mx-auto max-w-6xl">
        <div className="grid gap-6 lg:grid-cols-3">
          <motion.div 
            className="glass-elevated rounded-2xl p-6 lg:col-span-2"
            initial={{ y: 20, opacity: 0 }}
            whileInView={{ y: 0, opacity: 1 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
          >
            <h3 className="text-lg font-medium mb-4">Core Capabilities</h3>
            <motion.div 
              className="grid grid-cols-1 sm:grid-cols-2 gap-4"
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
            >
              {items.slice(0,4).map((it)=>{
                const Icon = it.icon
                return (
                  <motion.div 
                    key={it.title} 
                    variants={cardVariants}
                    whileHover={{ y: -4, scale: 1.02, boxShadow: "0 10px 30px var(--jade-glow)" }}
                    className="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-4 transition-all duration-300 cursor-pointer"
                  >
                    <div className="flex items-center gap-3">
                      <div className="rounded bg-[var(--bg-elevated)] p-2 shrink-0">
                        <Icon className="h-6 w-6 text-[var(--accent-cyan)]" />
                      </div>
                      <div>
                        <div className="font-medium text-sm sm:text-base text-[var(--text-primary)]">{it.title}</div>
                        <div className="text-xs text-[var(--text-muted)] mt-0.5">{it.desc}</div>
                      </div>
                    </div>
                  </motion.div>
                )
              })}
            </motion.div>
          </motion.div>

          <motion.div 
            className="glass rounded-2xl p-6"
            initial={{ y: 20, opacity: 0 }}
            whileInView={{ y: 0, opacity: 1 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94], delay: 0.15 }}
          >
            <h3 className="text-lg font-medium mb-4">Advanced Features</h3>
            <motion.div 
              className="space-y-3"
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
            >
              {items.slice(4).map(it=>{
                const Icon = it.icon
                return (
                  <motion.div 
                    key={it.title} 
                    variants={cardVariants}
                    whileHover={{ x: 4, background: "var(--glass-bg)" }}
                    className="flex items-start gap-3 rounded p-3 transition-all duration-200 cursor-pointer"
                  >
                    <div className="rounded bg-[var(--bg-elevated)] p-2 shrink-0">
                      <Icon className="h-5 w-5 text-[var(--accent-cyan)]" />
                    </div>
                    <div>
                      <div className="font-medium text-sm sm:text-base text-[var(--text-primary)]">{it.title}</div>
                      <div className="text-xs text-[var(--text-muted)] mt-0.5">{it.desc}</div>
                    </div>
                  </motion.div>
                )
              })}
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
