"use client"

import Link from "next/link"
import { useTheme } from "@/hooks/useTheme"

export default function Navbar() {
  const { theme, toggle } = useTheme()
  const isDark = theme === "dark"

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
        <button onClick={toggle} aria-label="Toggle theme" className="qs-btn-icon">{isDark ? "🌙" : "☀️"}</button>
      </nav>
    </header>
  )
}
