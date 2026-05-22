"use client"
import React, { Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import toast from 'react-hot-toast'

function OAuthCallbackInner() {
  const router = useRouter()
  const params = useSearchParams()

  React.useEffect(() => {
    const error = params.get('error')
    const status = params.get('status')
    const tempToken = params.get('temp_token')

    if (error) {
      toast.error(decodeURIComponent(error))
      router.replace('/auth/login')
      return
    }
    if (status === 'pending') {
      toast('Account created. Waiting for admin approval.', { icon: '⏳' })
      router.replace('/auth/login')
      return
    }
    if (tempToken) {
      try {
        localStorage.setItem('qs_temp_token', tempToken)
      } catch (_) {}
      router.replace('/auth/setup-2fa')
      return
    }
    toast.error('OAuth sign-in did not complete.')
    router.replace('/auth/login')
  }, [params, router])

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="glass p-8 rounded-lg text-center">
        <p className="text-ink-300">Completing sign-in…</p>
      </div>
    </div>
  )
}

export default function OAuthCallbackPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading…</div>}>
      <OAuthCallbackInner />
    </Suspense>
  )
}
