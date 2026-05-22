"use client"
import React from 'react'

export default function ResultTable({ columns, rows }:{columns:string[], rows:Record<string,any>[]}){
  return (
    <div className="glass p-4 rounded">
      <div className="overflow-x-auto">
        <table className="w-full table-auto border-separate" style={{borderSpacing:0}}>
          <thead>
            <tr className="bg-ink-800">
              {columns.map(c=> <th key={c} className="text-left py-3 px-3 text-ink-400 text-sm">{c}</th>)}
            </tr>
          </thead>
          <tbody>
            {rows.map((r,i)=> (
              <tr key={i} className={i%2===0? 'bg-white/2':'bg-transparent'}>
                {columns.map(col=> <td key={col} className="py-2 px-3 text-sm">{String(r[col] ?? 'null')}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
