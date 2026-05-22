"use client"
import React, {useState, useRef, useEffect} from 'react'
import api from '../../lib/api'
import ResultTable from './ResultTable'

export default function ChatPanel(){
  const [prompt, setPrompt] = useState('')
  const [loading, setLoading] = useState(false)
  const [sql, setSql] = useState<string | null>(null)
  const [rows, setRows] = useState<Array<Record<string, any>> | null>(null)
  const [columns, setColumns] = useState<string[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const controllerRef = useRef<AbortController | null>(null)
  const [cursorVisible, setCursorVisible] = useState(false)

  useEffect(()=>{
    let t: number | null = null
    if(loading){
      t = window.setInterval(()=> setCursorVisible(v=>!v), 500)
    } else {
      setCursorVisible(false)
      if(t) { clearInterval(t); t = null }
    }
    return ()=>{ if(t) clearInterval(t) }
  },[loading])

  // persist last generated SQL so Inspector can use it
  useEffect(()=>{
    if(typeof window === 'undefined') return
    try{
      if(sql !== null) localStorage.setItem('qs_last_sql', sql)
    }catch(e){}
  },[sql])

  async function send(){
    if(!prompt) return
    setLoading(true)
    setError(null)
    setSql(null)
    try{
      if(controllerRef.current) controllerRef.current.abort()
      const controller = new AbortController()
      controllerRef.current = controller
      // attempt streaming fetch for progressive SQL output
      const streamRes = await fetch('/api/ai/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
        signal: controller.signal,
      })

      // if response is a JSON payload, parse and fallback
      const contentType = streamRes.headers.get('content-type') || ''
      if(contentType.includes('application/json')){
        const data = await streamRes.json()
        if(data?.sql) setSql(data.sql)
        else if(typeof data === 'string') setSql(data)
        else setSql(JSON.stringify(data))
        if(Array.isArray(data?.rows)){
          setRows(data.rows)
          if(Array.isArray(data.columns)) setColumns(data.columns)
          else if(data.rows.length) setColumns(Object.keys(data.rows[0]))
        } else { setRows(null); setColumns(null) }
      } else if(streamRes.body){
        // stream text chunks
        const reader = streamRes.body.getReader()
        const decoder = new TextDecoder()
        let done = false
        let acc = ''
        while(!done){
          const { value, done: d } = await reader.read()
          done = d
          if(value){
            const chunk = decoder.decode(value, { stream: true })
            acc += chunk
            setSql(acc)
          }
        }
        // try to parse acc as JSON for rows
        try{
          const parsed = JSON.parse(acc)
          if(parsed?.rows) {
            setRows(parsed.rows)
            if(parsed.columns) setColumns(parsed.columns)
          }
        }catch(e){ /* not JSON, ignore */ }
      } else {
        setError('Empty response')
      }
    }
    catch(err:any){
      // fallback to axios if fetch fails
      try{
        const res = await api.post('/ai/generate', {prompt})
        const data = res?.data
        if(data?.sql) setSql(data.sql)
        else if(typeof data === 'string') setSql(data)
        else setSql(JSON.stringify(data))
        if(Array.isArray(data?.rows)){
          setRows(data.rows)
          if(Array.isArray(data.columns)) setColumns(data.columns)
          else if(data.rows.length) setColumns(Object.keys(data.rows[0]))
        } else { setRows(null); setColumns(null) }
      }catch(e:any){
        setError(e?.message || 'Request failed')
      }
    }finally{
      controllerRef.current = null
      setLoading(false)
    }
  }

  function stop(){
    if(controllerRef.current){
      controllerRef.current.abort()
      controllerRef.current = null
      setLoading(false)
      setError('Cancelled')
    }
  }

  async function copySql(){
    if(!sql) return
    try{ await navigator.clipboard.writeText(sql); alert('Copied SQL to clipboard') }catch(e){ alert('Copy failed') }
  }

  return (
    <div className="flex-1 p-6 overflow-auto">
      <div className="h-full flex flex-col">
        <div className="flex-1 bg-gradient-to-b from-transparent to-transparent p-4 rounded space-y-4">
          <div className="text-sm text-[--text-muted]">Chat history (mock)</div>
          <div className="space-y-3 mt-4">
            <div className="self-end bg-[--bg-elevated] p-3 rounded text-sm font-mono">{prompt || 'Show top customers this quarter'}</div>
            <div className="bg-[--bg-surface] p-3 rounded text-sm">
              <div className="text-xs text-[--text-muted]">{loading ? 'Generating SQL...' : (error ? 'Error' : 'Generated SQL')}</div>
              <pre className="sql-block">{loading ? (sql ?? '...') + (cursorVisible ? '|' : '') : (error ? error : (sql ?? 'No SQL yet'))}</pre>
            </div>
            {rows && columns && (
              <div className="mt-3">
                <ResultTable columns={columns} rows={rows} />
              </div>
            )}
          </div>
        </div>
        <div className="mt-4">
          <div className="p-3 bg-[--bg-surface] rounded flex items-center gap-3">
            <input value={prompt} onChange={e=>setPrompt(e.target.value)} className="qs-input flex-1" placeholder="Ask anything about your data..." />
            {loading ? (
              <button onClick={stop} className="qs-btn-ghost">Stop</button>
            ) : (
              <button onClick={send} className="qs-btn-primary" disabled={loading}>{loading ? '...' : 'Send'}</button>
            )}
            {!loading && sql && (
              <button onClick={copySql} className="qs-btn-ghost">Copy</button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
