"use client"
import React from 'react'
import Link from 'next/link'

export default function Navbar(){
  const [isDark, setIsDark] = React.useState<boolean>(false)

  React.useEffect(()=>{
    try{
      const saved = localStorage.getItem('theme')
      if(saved) setIsDark(saved === 'dark')
      else setIsDark(document.documentElement.classList.contains('dark'))
    }catch(e){}
  },[])

  const toggleTheme = ()=>{
    try{
      const next = !isDark
      setIsDark(next)
      if(next) {
        document.documentElement.classList.add('dark')
        localStorage.setItem('theme','dark')
      } else {
        document.documentElement.classList.remove('dark')
        localStorage.setItem('theme','light')
      }
    }catch(e){}
  }
  return (
    <header className="w-full glass p-4 flex items-center justify-between shadow-sm"> 
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded flex items-center justify-center bg-jade text-black font-bold">QS</div>
        <Link href="/" className="font-display text-lg">QuerySafe</Link>
      </div>
      <nav className="flex items-center gap-4 text-sm text-[var(--text-muted)]">
        <Link href="/dashboard" className="hover:text-[var(--text-primary)] transition-colors">Dashboard</Link>
        <Link href="/dashboard/charts" className="hover:text-[var(--text-primary)] transition-colors">Charts</Link>
        <Link href="/auth/login" className="px-3 py-1 border border-[var(--border-subtle)] rounded hover:bg-[var(--glass-highlight)] text-[var(--text-primary)] transition-all">Login</Link>
        <button onClick={toggleTheme} aria-label="Toggle theme" className="qs-btn-icon">
          {isDark ? '🌙' : '☀️'}
        </button>
      </nav>
    </header>
  )
}
