"use client"
import React from 'react'

export default function DBConnector({ onConnectionChange }:{onConnectionChange?: (id:string|null)=>void}){
  return (
    <div className="glass p-4 rounded">
      <h3 className="font-medium mb-3">DB Connector</h3>
      <form onSubmit={(e)=>e.preventDefault()} className="space-y-2">
        <label className="text-sm text-ink-400">Type</label>
        <select className="qs-input">
          <option>PostgreSQL</option>
          <option>MySQL</option>
          <option>MongoDB</option>
        </select>
        <label className="text-sm text-ink-400">Host</label>
        <input className="qs-input" placeholder="localhost" />
        <label className="text-sm text-ink-400">Database</label>
        <input className="qs-input" placeholder="mydb" />
        <button className="qs-btn-primary w-full">Connect</button>
      </form>
    </div>
  )
}
