"use client"
import React from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'

const toastOptions = {
  style: {
    background: '#121228',
    color: '#B0B0C8',
    border: '1px solid rgba(255,255,255,0.08)',
    borderRadius: '12px',
    fontSize: '13px',
    backdropFilter: 'blur(16px)',
    boxShadow: '0 8px 40px rgba(0,0,0,0.4)',
  },
  success: {
    iconTheme: { primary: '#00C896', secondary: '#000' },
  },
  error: {
    iconTheme: { primary: '#FF3B5C', secondary: '#fff' },
  },
}

export default function ClientProviders({ children }: { children: React.ReactNode }) {
  const [queryClient] = React.useState(() => new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        retry: 2,
      },
    },
  }))

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <Toaster position="top-right" toastOptions={toastOptions} />
    </QueryClientProvider>
  )
}
