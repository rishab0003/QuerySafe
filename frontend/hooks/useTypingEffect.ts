import { useEffect, useState } from 'react'

/**
 * Simulates typing animation by revealing characters one by one.
 * @param text   Full text to type out.
 * @param speed  Milliseconds per character (default 40ms).
 * @returns      The currently displayed substring.
 */
export function useTypingEffect(text: string, speed: number = 40): string {
  const [displayed, setDisplayed] = useState('')

  useEffect(() => {
    let i = 0
    const interval = setInterval(() => {
      setDisplayed(text.slice(0, i + 1))
      i++
      if (i >= text.length) clearInterval(interval)
    }, speed)
    return () => clearInterval(interval)
  }, [text, speed])

  return displayed
}
