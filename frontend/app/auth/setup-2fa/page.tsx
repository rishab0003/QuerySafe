"use client"
import React from 'react'
import api from '../../../lib/api'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import useAuthStore from '../../../lib/store'

export default function Setup2FA(){
  const router = useRouter()
  const [loading, setLoading] = React.useState(false)
  const [qr, setQr] = React.useState<string | null>(null)
  const [secret, setSecret] = React.useState<string | null>(null)
  const [method, setMethod] = React.useState<'qr' | 'email'>('qr')
  const [code, setCode] = React.useState('')
  const [email, setEmail] = React.useState('')
  const [redirectSeconds, setRedirectSeconds] = React.useState<number | null>(null)
  const redirectTimerRef = React.useRef<number | null>(null)

  React.useEffect(()=>{
    const temp = typeof window !== 'undefined' ? localStorage.getItem('qs_temp_token') : null
    if(temp) {
      fetchSetup({ temp_token: temp })
      return
    }

    // No temp token: start auto-redirect countdown unless user enters an email
    setRedirectSeconds(8)
    redirectTimerRef.current = window.setInterval(()=>{
      setRedirectSeconds(s => {
        if(s === null) return null
        if(s <= 1) {
          if(redirectTimerRef.current) {
            clearInterval(redirectTimerRef.current)
            redirectTimerRef.current = null
          }
          router.push('/auth/login')
          return 0
        }
        return s - 1
      })
    }, 1000)

    return ()=>{
      if(redirectTimerRef.current) { clearInterval(redirectTimerRef.current); redirectTimerRef.current = null }
    }
  },[])

  async function fetchSetup(payload: { temp_token?: string; email?: string }){
    setLoading(true)
    const id = toast.loading('Requesting 2FA setup...')
    try{
      const res = await api.post('/auth/setup-2fa', { ...payload, method })
      const body = res.data
      setQr(body.qr_code_base64 ? `data:image/png;base64,${body.qr_code_base64}` : null)
      setSecret(body.secret || null)
      if(body.otp_code) {
        toast.success('OTP generated; check email or use shown code')
      }
      toast.dismiss(id)
      toast.success('2FA setup ready')
    }catch(err: any){
      toast.dismiss(id)
      toast.error(err?.response?.data?.detail || 'Setup failed')
    }finally{ setLoading(false) }
  }

  async function handleRequestSetup(e: React.FormEvent){
    e.preventDefault()
    if(!email) return toast.error('Enter email')
    // If a redirect timer is running, cancel it because user is actively requesting setup
    if(redirectTimerRef.current) { clearInterval(redirectTimerRef.current); redirectTimerRef.current = null }
    setRedirectSeconds(null)
    await fetchSetup({ email })
  }

  async function handleVerify(e: React.FormEvent){
    e.preventDefault()
    setLoading(true)
    const id = toast.loading('Verifying code...')
    try{
      const temp = typeof window !== 'undefined' ? localStorage.getItem('qs_temp_token') : null
      const payload: any = { code }
      if(temp) payload.temp_token = temp
      else payload.temp_token = undefined
      const res = await api.post('/auth/verify-2fa', payload)
      const body = res.data
      if(body.access_token) {
        try{ localStorage.setItem('qs_token', body.access_token) }catch(e){}
        useAuthStore.getState().setToken(body.access_token)
      }
      if(body.refresh_token) try{ localStorage.setItem('qs_refresh', body.refresh_token) }catch(e){}
      try {
        const me = await api.get('/auth/me')
        useAuthStore.getState().setUser(me.data)
      } catch (_) {}
      toast.dismiss(id)
      toast.success('2FA verified')
      setLoading(false)
      router.push('/dashboard')
    }catch(err: any){
      toast.dismiss(id)
      toast.error(err?.response?.data?.detail || 'Verification failed')
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md glass p-8 rounded-lg">
        <h2 className="text-2xl font-display mb-4">Setup 2FA</h2>
        {!qr && (
          <form onSubmit={handleRequestSetup} className="space-y-3">
            <p className="text-sm text-ink-400 mb-2">Choose setup method and enter your email.</p>
            <div className="flex gap-3 mb-2">
              <label className="inline-flex items-center"><input type="radio" name="method" checked={method==='qr'} onChange={()=>setMethod('qr')} /> <span className="ml-2">Authenticator App (QR)</span></label>
              <label className="inline-flex items-center"><input type="radio" name="method" checked={method==='email'} onChange={()=>setMethod('email')} /> <span className="ml-2">Email OTP</span></label>
            </div>
            <input className="qs-input" placeholder="you@example.com" value={email} onChange={(e)=>setEmail(e.target.value)} disabled={loading} />
            <button className="qs-btn-primary w-full" disabled={loading}>Request</button>
          </form>
        )}

        {qr && (
          <form onSubmit={handleVerify} className="space-y-3">
            <p className="text-sm text-ink-400">Scan the QR with your authenticator app and enter the 6-digit code.</p>
            <div className="mb-4 p-4 bg-white/4 rounded flex items-center justify-center">
              {qr ? <img src={qr} alt="2FA QR" /> : <div className="text-ink-400">QR not available</div>}
            </div>
            {secret && <div className="text-xs text-ink-400 mb-1">Secret: {secret}</div>}
            <input className="qs-input" placeholder="123456" value={code} onChange={(e)=>setCode(e.target.value)} disabled={loading} />
            <button className="qs-btn-primary w-full" disabled={loading}>Verify</button>
          </form>
        )}
        {/* If OTP was returned directly (dev fallback), show it for convenience */}
        {/* Note: this is only displayed if backend returns otp_code as part of setup response */}
        {/* The verify form above will still accept the code */}
      </div>
    </div>
  )
}
