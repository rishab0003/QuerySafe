"use client"
import React from 'react'

const PRESETS = [
  'DROP TABLE users',
  'DELETE all records',
  'Show my salary',
]

function isDangerous(input: string){
  const s = input.toLowerCase()
  const destructive = ['drop','delete','truncate','alter','shutdown']
  for(const kw of destructive) if(s.includes(kw)) return { dangerous: true, reason: `Contains ${kw.toUpperCase()} — destructive operation forbidden` }
  if(s.match(/my\s+salary|show\s+my\s+salary/)) return { dangerous: true, reason: 'Personal data request — blocked by policy' }
  return { dangerous: false }
}

export default function AttackDemo(){
  const [input, setInput] = React.useState('')
  const [status, setStatus] = React.useState<{type:'idle'|'safe'|'blocked','reason'?:string}>(()=>({type:'idle'}))

  function runQuery(q?:string){
    const txt = q ?? input
    const res = isDangerous(txt)
    if(res.dangerous) setStatus({ type:'blocked', reason: res.reason })
    else setStatus({ type:'safe' })
  }

  return (
    <div className="glass w-full max-w-xl rounded-2xl p-5 sm:p-6">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div className="font-medium">See the Safety Engine in Action</div>
        <div className="text-xs text-[--text-muted]">Try presets</div>
      </div>

      <div className="mb-3 flex flex-wrap gap-2">
        {PRESETS.map(p=> (
          <button key={p} onClick={()=>{ setInput(p); runQuery(p) }} className="qs-btn-ghost whitespace-nowrap text-xs">{p}</button>
        ))}
      </div>

      <textarea value={input} onChange={(e)=>{ setInput(e.target.value); setStatus({type:'idle'}) }} className="qs-input mb-3 h-24" placeholder="Type SQL or natural language" />

      <div className="flex flex-wrap items-center gap-3">
        <button className="qs-btn-primary" onClick={()=>runQuery()}>Analyze</button>
        {status.type === 'blocked' && (
          <div className="ml-auto text-sm text-[--accent-red] flex items-center gap-2 animate-shake">
            ⚠ BLOCKED — {status.reason}
          </div>
        )}
        {status.type === 'safe' && (
          <div className="ml-auto text-sm text-[--accent-green] flex items-center gap-2">
            ✓ SAFE — SQL preview below
          </div>
        )}
      </div>

      {status.type === 'safe' && (
        <div className="mt-4 rounded border border-[var(--border-subtle)] bg-[var(--bg-elevated)] p-3">
          <div className="text-xs text-[--accent-green] mb-1">SQL Preview</div>
          <pre className="sql-block">-- Mock SQL result
SELECT * FROM invoices WHERE amount &gt; 50000;</pre>
        </div>
      )}
    </div>
  )
}
