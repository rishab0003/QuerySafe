import React from 'react'
import Link from 'next/link'
import AnimatedBackground from '../components/ui/AnimatedBackground'

export default function Home(){
  return (
    <main className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-4xl w-full">
        <AnimatedBackground />
        <section className="glass p-8 rounded-lg">
          <h1 className="text-4xl font-display font-extrabold mb-2">QuerySafe</h1>
          <p className="text-ink-400 mb-6">AI-powered Natural Language Database Interface — Demo frontend</p>
          <div className="flex gap-4">
            <Link href="/auth/login" className="qs-btn-primary">Login</Link>
            <Link href="/dashboard" className="qs-btn-ghost">Dashboard</Link>
          </div>
        </section>
      </div>
    </main>
  )
}
