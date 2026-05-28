import { useRef } from 'react'
import { useInView } from 'framer-motion'
import { useMotionValue, useSpring, useTransform } from 'framer-motion'

/**
 * Animated counter that starts counting when the element scrolls into view.
 * @param target Target number to count to.
 * @returns {ref, display} where `ref` should be attached to the element and `display` is an animated string.
 */
export function useAnimatedCounter(target: number) {
  const ref = useRef(null)
  const inView = useInView(ref, { once: true })

  const motionValue = useMotionValue(0)
  const spring = useSpring(motionValue, { damping: 20, stiffness: 120 })
  const display = useTransform(spring, (value) => Math.round(value).toLocaleString())

  if (inView) {
    motionValue.set(target)
  }

  return { ref, display }
}
