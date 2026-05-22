"use client"
import React from 'react'
import {useRouter} from 'next/navigation'
import Sidebar from '../../components/dashboard/Sidebar'
import ChatPanel from '../../components/dashboard/ChatPanel'
import Inspector from '../../components/dashboard/Inspector'
import useAuthStore from '../../lib/store'

export default function DashboardPage(){
  const router = useRouter()
  const token = useAuthStore(s=>s.token)

  React.useEffect(()=>{
    if(typeof window === 'undefined') return
    const t = localStorage.getItem('qs_token')
    if(!t) router.replace('/auth/login')
  },[router, token])

  return (
    <div className="min-h-screen flex bg-[--bg-void] text-[--text-primary]">
      <Sidebar />
      <main className="flex-1 flex flex-col">
        <ChatPanel />
      </main>
      <Inspector />
    </div>
  )
}
 
