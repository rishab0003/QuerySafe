"use client"
import React from 'react'
import { useRouter } from 'next/navigation'

export default function LoginPage(){
  const router = useRouter()
  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md glass p-8 rounded-lg">
        <h2 className="text-2xl font-display mb-4">Sign in to QuerySafe</h2>
        <form onSubmit={(e)=>{e.preventDefault(); router.push('/auth/setup-2fa')}} className="space-y-3">
          <div>
            <label className="block mb-1 text-sm text-ink-400">Email</label>
            <input className="qs-input" placeholder="demo@example.com" />
          </div>
          <div>
            <label className="block mb-1 text-sm text-ink-400">Password</label>
            <input type="password" className="qs-input" placeholder="password" />
          </div>
          <button className="qs-btn-primary w-full">Sign in</button>
        </form>
      </div>
    </div>
  )
}
