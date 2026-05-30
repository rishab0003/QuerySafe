import React from 'react'
import Sidebar from '../../components/dashboard/Sidebar'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col lg:flex-row bg-[var(--bg-void)] text-[var(--text-primary)] overflow-x-hidden">
      <Sidebar />
      <main className="flex-1 flex flex-col min-h-0 overflow-auto w-full">
        {children}
      </main>
    </div>
  )
}
