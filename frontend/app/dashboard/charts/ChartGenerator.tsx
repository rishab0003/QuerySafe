"use client"
import React, {useState} from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

export default function ChartGenerator(){
  const [prompt, setPrompt] = useState('')
  const [data, setData] = useState<any[]>([])

  function generate(){
    // Mock simple generated data
    const d = Array.from({length:7}).map((_,i)=>({name:`Day ${i+1}`, value: Math.round(Math.random()*100)}))
    setData(d)
  }

  return (
    <div className="glass p-4 rounded">
      <div className="flex gap-2 mb-3">
        <input className="flex-1 p-2 bg-transparent border rounded" value={prompt} onChange={(e)=>setPrompt(e.target.value)} placeholder="Generate a line chart of signups this week" />
        <button onClick={generate} className="px-4 py-2 bg-[#00C896] rounded">Generate</button>
      </div>
      {data.length>0 && (
        <div style={{height:300}}>
          <ResponsiveContainer>
            <LineChart data={data}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="value" stroke="#00C896" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
