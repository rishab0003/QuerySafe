"use client"
import React from 'react'

export default function RegisterPage(){
  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md glass p-8 rounded-lg">
        <h2 className="text-2xl font-display mb-4">Create account</h2>
        <form className="space-y-3">
          <div>
            <label className="block mb-1 text-sm text-ink-400">Name</label>
            <input className="qs-input" />
          </div>
          <div>
            <label className="block mb-1 text-sm text-ink-400">Email</label>
            <input className="qs-input" />
          </div>
          <div>
            <label className="block mb-1 text-sm text-ink-400">Password</label>
            <input type="password" className="qs-input" />
          </div>
          <button className="qs-btn-primary w-full">Create account</button>
        </form>
      </div>
    </div>
  )
}
