"use client"
import React from 'react'

export default function Setup2FA(){
  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md glass p-8 rounded-lg">
        <h2 className="text-2xl font-display mb-4">Setup 2FA</h2>
        <p className="text-sm text-ink-400 mb-4">Scan the QR with your authenticator app and enter the 6-digit code.</p>
        <div className="mb-4 p-4 bg-white/4 rounded flex items-center justify-center">[QR]</div>
        <input className="qs-input mb-2" placeholder="123456" />
        <button className="qs-btn-primary w-full">Verify</button>
      </div>
    </div>
  )
}
