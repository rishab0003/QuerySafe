"use client"
import React from 'react'
import { useState, useEffect } from 'react'
import api from '../../lib/api'
import toast from 'react-hot-toast'

export default function Inspector(){
  const [sql, setSql] = useState<string>('')
  const [explain, setExplain] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(()=>{
    try{
      const last = typeof window !== 'undefined' ? localStorage.getItem('qs_last_sql') : null
      if(last) setSql(last)
    }catch(e){}
  },[])

  async function explainSql(){
    if(!sql) return toast.error('No SQL to explain')
    setLoading(true)
    setExplain(null)
    try{
      const res = await api.post('/ai/explain', { sql })
      const data = res?.data
      if(typeof data === 'string') setExplain(data)
      else if(data?.explanation) setExplain(data.explanation)
      else setExplain(JSON.stringify(data))
    }catch(err:any){
      toast.error(err?.response?.data?.detail || err?.message || 'Explain failed')
    }finally{ setLoading(false) }
  }

  async function copyExplain(){
    if(!explain) return
    try{ await navigator.clipboard.writeText(explain); toast.success('Copied explanation') }catch(e){ toast.error('Copy failed') }
  }

  return (
    <aside className="w-80 bg-[--bg-elevated] p-4 h-screen overflow-auto">
      <div className="font-medium mb-3">SQL Inspector</div>
      <textarea className="w-full font-mono p-2 bg-[#06070b] text-white rounded" rows={6} value={sql} onChange={e=>setSql(e.target.value)} />
      <div className="mt-3 text-sm text-[--text-muted]">Edit SQL or use the last generated query.</div>
      <div className="mt-4 space-y-2">
        <button onClick={explainSql} className="qs-btn-primary w-full" disabled={loading}>{loading ? 'Explaining…' : 'Explain this SQL'}</button>
        <button onClick={copyExplain} className="qs-btn-ghost w-full" disabled={!explain}>Copy explanation</button>
      </div>
      {explain && (
        <div className="mt-4 p-3 bg-[--bg-surface] rounded text-sm whitespace-pre-wrap">{explain}</div>
      )}
    </aside>
  )
}
