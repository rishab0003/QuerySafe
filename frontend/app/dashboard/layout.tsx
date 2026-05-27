import React from 'react'
import Sidebar from '../../components/dashboard/Sidebar'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex bg-[var(--bg-void)] text-[var(--text-primary)]">
      <Sidebar />
      <main className="flex-1 flex flex-col min-h-0 overflow-auto">
        {children}
      </main>
    </div>
  )
}
