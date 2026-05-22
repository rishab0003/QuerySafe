import React from 'react'
import Navbar from '../../components/layout/Navbar'

export default function DashboardLayout({ children }: { children: React.ReactNode }){
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="p-6">{children}</main>
    </div>
  )
}
