"use client"
import React from 'react'
import Link from 'next/link'

export default function Navbar(){
  return (
    <header className="w-full glass p-4 flex items-center justify-between shadow-sm"> 
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded flex items-center justify-center bg-jade text-black font-bold">QS</div>
        <Link href="/" className="font-display text-lg">QuerySafe</Link>
      </div>
      <nav className="flex items-center gap-4 text-sm text-ink-400">
        <Link href="/dashboard" className="hover:text-white">Dashboard</Link>
        <Link href="/dashboard/charts" className="hover:text-white">Charts</Link>
        <Link href="/auth/login" className="px-3 py-1 border border-white/10 rounded hover:bg-white/2">Login</Link>
      </nav>
    </header>
  )
}
