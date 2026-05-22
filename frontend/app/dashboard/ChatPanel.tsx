"use client"
import React, {useState} from 'react'
import ExplainDrawer from '../../components/dashboard/ExplainDrawer'

export default function ChatPanel(){
  const [messages, setMessages] = useState<Array<any>>([])
  const [input, setInput] = useState('')
  const [explainData, setExplainData] = useState<any|null>(null)

  function send(){
    if(!input) return
    const userMsg = {role:'user', text: input}
    // Mock AI response for demo
    const ai = {role:'ai', text: `Mock answer for: ${input}`, sql: `SELECT * FROM users WHERE name LIKE '%${input}%'`, confidence: 92}
    setMessages(prev=>[...prev, userMsg, ai])
    setInput('')
  }

  return (
    <div>
      <div className="glass p-4 rounded mb-4">
        <div className="space-y-3 max-h-80 overflow-auto scrollbar-thin">
          {messages.map((m,i)=> (
            <div key={i} className={m.role==='user'? 'flex justify-end':'flex justify-start'}>
              <div className={(m.role==='user'? 'bg-jade text-black':'bg-white/6 text-white') + ' max-w-[70%] p-3 rounded-lg'}>
                <div className="text-sm">{m.text || JSON.stringify(m)}</div>
                {m.sql && (
                  <div className="mt-2">
                    <div className="sql-block">{m.sql}</div>
                    <div className="mt-2 flex gap-2">
                      <button onClick={()=>setExplainData(m)} className="px-2 py-1 border border-white/8 rounded text-sm">Explain</button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
      <div className="flex gap-2">
        <input value={input} onChange={(e)=>setInput(e.target.value)} className="qs-input" placeholder="Ask in plain English" />
        <button onClick={send} className="qs-btn-primary">Send</button>
      </div>
      <ExplainDrawer data={explainData} onClose={()=>setExplainData(null)} />
    </div>
  )
}
