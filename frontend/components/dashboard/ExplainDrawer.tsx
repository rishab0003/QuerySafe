"use client"
import React from 'react'

export default function ExplainDrawer({ data, onClose }:{data:any|null,onClose?:()=>void}){
  if(!data) return null
  return (
    <aside className="fixed right-0 top-0 h-full w-96 bg-[#0b0b12] p-4 shadow-lg">
      <button onClick={onClose} className="mb-3 px-2 py-1 border rounded">Close</button>
      <pre className="whitespace-pre-wrap text-sm">{JSON.stringify(data,null,2)}</pre>
    </aside>
  )
}
