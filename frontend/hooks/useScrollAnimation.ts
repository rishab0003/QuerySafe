import { useRef } from 'react'
import { useInView } from 'framer-motion'

/**
 * Hook that returns a ref to attach to a DOM element and a boolean indicating
 * whether the element is in view. It uses Framer Motion's `useInView` with the
 * `once` option so the animation only triggers the first time the element
 * enters the viewport.
 *
 * @param margin – viewport margin (e.g. '-80px')
 */
export function useScrollAnimation(margin: string = '-80px') {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true, margin })
  return { ref, inView }
}
