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
      <div className="max-w-6xl mx-auto">
        <div className="grid lg:grid-cols-3 gap-6">
          <motion.div className="glass-elevated p-6 rounded-2xl lg:col-span-2" initial={{ y:12, opacity:0 }} animate={{ y:0, opacity:1 }}>
            <h3 className="text-lg font-medium mb-4">Core Capabilities</h3>
            <div className="grid grid-cols-2 gap-4">
              {items.slice(0,4).map((it,idx)=>{
                const Icon = it.icon
                return (
                  <div key={it.title} className="p-4 rounded-lg hover:shadow-jade-glow transition transform hover:-translate-y-1 border border-[--border-subtle] bg-gradient-to-b from-transparent to-transparent">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded bg-[#071018]">
                        <Icon className="w-6 h-6 text-[--accent-cyan]" />
                      </div>
                      <div>
                        <div className="font-medium">{it.title}</div>
                        <div className="text-xs text-[--text-muted]">{it.desc}</div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </motion.div>

          <motion.div className="glass p-6 rounded-2xl" initial={{ y:12, opacity:0 }} animate={{ y:0, opacity:1 }}>
            <h3 className="text-lg font-medium mb-4">Advanced Features</h3>
            <div className="space-y-3">
              {items.slice(4).map(it=>{
                const Icon = it.icon
                return (
                  <div key={it.title} className="flex items-start gap-3 p-3 rounded hover:bg-white/2 transition">
                    <div className="p-2 rounded bg-[#071018]">
                      <Icon className="w-5 h-5 text-[--accent-cyan]" />
                    </div>
                    <div>
                      <div className="font-medium">{it.title}</div>
                      <div className="text-xs text-[--text-muted]">{it.desc}</div>
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
