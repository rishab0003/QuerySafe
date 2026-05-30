"use client"
import React from 'react'

type Props = {
  columns: string[]
  rows: Array<Record<string, any>>
}

export default function ResultTable({columns, rows}: Props){
  return (
    <div className="overflow-auto bg-[--bg-surface] rounded p-3 max-w-full">
      <table className="w-full min-w-max text-sm table-auto">
        <thead>
          <tr>
            {columns.map(col=> (
              <th key={col} className="text-left pr-4 pb-2 text-[--text-muted]">{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r,idx)=> (
            <tr key={idx} className={idx%2? 'bg-[--bg-elevated]':''}>
              {columns.map(col=> (
                <td key={col} className="py-2 pr-4 font-mono">{String(r[col] ?? '')}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
