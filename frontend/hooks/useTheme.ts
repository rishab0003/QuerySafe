// Hook to handle light/dark theme syncing with localStorage and system preference
import { useEffect, useState } from 'react'

export type Theme = 'light' | 'dark'

export function useTheme() {
  const [theme, setTheme] = useState<Theme>('light')

  // Initialise from localStorage or system preference
  useEffect(() => {
    try {
      const saved = localStorage.getItem('theme') as Theme | null
      if (saved) {
        setTheme(saved)
        if (saved === 'dark') document.documentElement.classList.add('dark')
        else document.documentElement.classList.remove('dark')
      } else {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        const initial: Theme = prefersDark ? 'dark' : 'light'
        setTheme(initial)
        if (initial === 'dark') document.documentElement.classList.add('dark')
      }
    } catch {}
  }, [])

  const toggle = () => {
    const next = theme === 'dark' ? 'light' : 'dark'
    setTheme(next)
    if (next === 'dark') {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  return { theme, toggle }
}
