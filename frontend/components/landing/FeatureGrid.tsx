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

export default function FeatureGrid(){
  return (
    <section className="px-6 pb-24">
      <div className="mx-auto max-w-6xl">
        <div className="grid gap-6 lg:grid-cols-3">
          <motion.div className="glass-elevated rounded-2xl p-6 lg:col-span-2" initial={{ y:12, opacity:0 }} animate={{ y:0, opacity:1 }}>
            <h3 className="text-lg font-medium mb-4">Core Capabilities</h3>
            <div className="grid grid-cols-2 gap-4">
              {items.slice(0,4).map((it,idx)=>{
                const Icon = it.icon
                return (
                  <div key={it.title} className="rounded-lg border border-[var(--border-subtle)] bg-[var(--bg-surface)] p-4 transition transform hover:-translate-y-1 hover:shadow-jade-glow">
                    <div className="flex items-center gap-3">
                      <div className="rounded bg-[var(--bg-elevated)] p-2">
                        <Icon className="h-6 w-6 text-[var(--accent-cyan)]" />
                      </div>
                      <div>
                        <div className="font-medium">{it.title}</div>
                        <div className="text-xs text-[var(--text-muted)]">{it.desc}</div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </motion.div>

          <motion.div className="glass rounded-2xl p-6" initial={{ y:12, opacity:0 }} animate={{ y:0, opacity:1 }}>
            <h3 className="text-lg font-medium mb-4">Advanced Features</h3>
            <div className="space-y-3">
              {items.slice(4).map(it=>{
                const Icon = it.icon
                return (
                  <div key={it.title} className="flex items-start gap-3 rounded p-3 transition hover:bg-[var(--glass-highlight)]">
                    <div className="rounded bg-[var(--bg-elevated)] p-2">
                      <Icon className="h-5 w-5 text-[var(--accent-cyan)]" />
                    </div>
                    <div>
                      <div className="font-medium">{it.title}</div>
                      <div className="text-xs text-[var(--text-muted)]">{it.desc}</div>
                    </div>
                  </div>
                )
              })}
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
