"use client"
import React from 'react'
import { motion } from 'framer-motion'

function Typewriter({ text = '', speed = 30 }: { text:string; speed?:number }){
  const [display, setDisplay] = React.useState('')
  React.useEffect(()=>{
    let i = 0
    const t = setInterval(()=>{
      setDisplay(text.slice(0, i))
      i++
      if(i > text.length) clearInterval(t)
    }, speed)
    return ()=>clearInterval(t)
  },[text,speed])
  return <span className="font-mono">{display}</span>
}

export default function Hero(){
  return (
    <section className="min-h-screen flex items-center justify-center relative overflow-hidden" aria-hidden>
      <div className="absolute inset-0 bg-gradient-to-b from-[--bg-void] to-[--bg-surface] opacity-80" />

      <div className="relative z-10 w-full max-w-6xl px-6 py-24 flex gap-12">
        <div className="flex-1">
          <motion.h1 className="font-display text-[72px] leading-[0.9] text-[--text-primary]" initial={{ y: 24, opacity: 0 }} animate={{ y:0, opacity:1 }} transition={{ delay:0.1 }}>
            <div>Your Database</div>
            <div className="bg-clip-text text-transparent" style={{ backgroundImage: 'linear-gradient(90deg,var(--accent-cyan),var(--accent-green))' }}>Speaks Human.</div>
            <div className="text-transparent stroke-text mt-1" style={{ WebkitTextStroke: '1px rgba(230,237,243,0.12)' }}>Securely.</div>
          </motion.h1>
          <motion.p className="mt-6 text-lg text-[--text-muted] max-w-xl" initial={{ y: 12, opacity: 0 }} animate={{ y:0, opacity:1 }} transition={{ delay:0.3 }}>
            Ask plain English. Get instant, encrypted, read-only answers.
          </motion.p>

          <motion.div className="mt-8 flex items-center gap-4" initial={{ opacity:0 }} animate={{ opacity:1 }} transition={{ delay:0.5 }}>
            <button className="qs-btn-primary">Get Started →</button>
            <button className="qs-btn-ghost flex items-center gap-2">▸ Watch Demo</button>
          </motion.div>
        </div>

        <div className="w-2/5">
          <div className="glass p-4 rounded-lg shadow-elevated">
            <div className="mb-2 text-sm text-[--text-muted]">Demo</div>
            <div className="bg-[#060712] p-3 rounded font-mono text-sm text-[--text-muted]">
              <div className="mb-2">User: <Typewriter text={'Show all invoices above ₹50,000 this month'} speed={28} /></div>
              <div className="mt-2 p-3 bg-[#071019] rounded border border-[--border-subtle]">
                <div className="text-xs text-[--accent-green] mb-1">SQL (generated)</div>
                <pre className="sql-block">SELECT * FROM invoices WHERE amount &gt; 50000 AND date_trunc('month', issued_at) = date_trunc('month', CURRENT_DATE);</pre>
                <div className="mt-2 flex items-center justify-between text-xs text-[--text-muted]">
                  <div className="badge qs-chip qs-chip-jade">98% confidence</div>
                  <div className="badge text-[--accent-green]">READ ONLY ✓</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="absolute inset-0 pointer-events-none">
        <div className="particle-grid" />
      </div>
    </section>
  )
}
