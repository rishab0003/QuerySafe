import './globals.css'
import React from 'react'
import ClientProviders from '../components/ClientProviders'

export const metadata = {
  title: 'QuerySafe',
  description: 'AI-powered natural language DB interface'
}

export default function RootLayout({ children }: { children: React.ReactNode }){
  return (
    <html lang="en">
      <body>
        <ClientProviders>
          <div className="min-h-screen">{children}</div>
        </ClientProviders>
      </body>
    </html>
  )
}
