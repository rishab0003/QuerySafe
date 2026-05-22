"use client"
import React from 'react'

const nodes = [
  { id:'prompt', label:'User Prompt', color:'--accent-cyan' },
  { id:'auth', label:'2FA Auth', color:'--accent-amber' },
  { id:'rbac', label:'RBAC Check', color:'--accent-green' },
  { id:'ai', label:'AI Engine', color:'--accent-cyan' },
  { id:'validator', label:'SQL Validator', color:'--accent-green' },
  { id:'db', label:'Read-Only DB', color:'--purple' },
  { id:'audit', label:'Audit Log', color:'--text-muted' },
]

export default function Pipeline(){
  return (
    <section className="px-6 pb-12">
      <div className="max-w-6xl mx-auto">
        <h3 className="text-lg font-medium mb-4">AI Pipeline</h3>
        <div className="glass p-6 rounded-2xl overflow-hidden">
          <div className="flex items-center gap-4 relative">
            <div className="moving-dot" />
            {nodes.map((n, i)=> (
              <div key={n.id} className="pipeline-node" title={n.label} style={{ ['--node-color' as any]: `var(${n.color})` }}>
                <div className="node-label">{n.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
