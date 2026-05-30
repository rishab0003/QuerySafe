"use client"
import React from 'react'
import toast from 'react-hot-toast'

function escapeHtml(unsafe: string){
  return unsafe.replace(/[&<>"']/g, function(m){
    switch(m){
      case '&': return '&amp;'
      case '<': return '&lt;'
      case '>': return '&gt;'
      case '"': return '&quot;'
      case "'": return '&#039;'
      default: return m
    }
  })
}

function highlightSQL(sql: string){
  if(!sql) return ''
  const keywords = ['SELECT','FROM','WHERE','JOIN','ON','INSERT','INTO','VALUES','UPDATE','SET','DELETE','CREATE','TABLE','ALTER','DROP','AND','OR','NOT','AS','ORDER','BY','GROUP','HAVING','LIMIT']
  let out = escapeHtml(sql)
  keywords.forEach(k=>{
    const re = new RegExp('\\b'+k+'\\b','gi')
    out = out.replace(re, (m)=>`<span class="keyword">${m}</span>`)
  })
  // strings
  out = out.replace(/('[^']*')/g, '<span class="string">$1</span>')
  // numbers
  out = out.replace(/(\b\d+\b)/g, '<span class="number">$1</span>')
  return out
}

export default function ExplainDrawer({ data, onClose }:{data:any|null,onClose?:()=>void}){
  if(!data) return null
  const sql = typeof data === 'string' ? data : (data.sql || JSON.stringify(data,null,2))

  const copy = async ()=>{
    try{
      await navigator.clipboard.writeText(typeof sql === 'string' ? sql : JSON.stringify(sql))
      toast.success('Copied SQL to clipboard')
    }catch(e){
      toast.error('Copy failed')
    }
  }

  return (
    <aside className="fixed inset-x-0 top-0 z-50 h-full w-full lg:left-auto lg:right-0 lg:inset-x-auto lg:w-96 bg-[#0b0b12] p-4 shadow-lg overflow-y-auto">
      <div className="flex items-center justify-between mb-3 gap-3">
        <div className="text-lg font-medium">Explanation</div>
        <div className="flex items-center gap-2">
          <button onClick={copy} className="qs-btn-ghost">Copy</button>
          <button onClick={onClose} className="qs-btn-ghost">Close</button>
        </div>
      </div>
      <div className="sql-block" dangerouslySetInnerHTML={{ __html: highlightSQL(typeof sql === 'string' ? sql : JSON.stringify(sql,null,2)) }} />
    </aside>
  )
}
