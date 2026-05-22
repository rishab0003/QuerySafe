import './globals.css'
import React from 'react'
import ClientProviders from '../components/ClientProviders'
import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'QuerySafe — AI-Powered Database Interface',
  description: 'Securely query your database using natural language. AI-powered SQL generation with role-based access control and enterprise-grade security.',
  keywords: ['SQL', 'AI', 'database', 'natural language', 'query', 'security'],
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const setThemeScript = `
    (function(){
      try{
        const theme = localStorage.getItem('theme');
        if(theme === 'dark') document.documentElement.classList.add('dark');
        else if(theme === 'light') document.documentElement.classList.remove('dark');
        else if(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
          document.documentElement.classList.add('dark');
        }
      }catch(e){/* noop */}
    })();
  `

  return (
    <html lang="en">
      <head>
        <script dangerouslySetInnerHTML={{ __html: setThemeScript }} />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="bg-ink text-white overflow-hidden">
        <ClientProviders>
          {children}
        </ClientProviders>
      </body>
    </html>
  )
}
