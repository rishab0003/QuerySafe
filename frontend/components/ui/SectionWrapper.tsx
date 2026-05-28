import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { fadeUp } from '@/lib/motion'

interface SectionWrapperProps {
  children: React.ReactNode
  id?: string
  className?: string
}

export default function SectionWrapper({ children, id, className }: SectionWrapperProps) {
  return (
    <motion.section
      id={id}
      variants={fadeUp}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-100px' }}
      className={cn(
        'relative py-24 lg:py-32 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto',
        className
      )}
    >
      {children}
    </motion.section>
  )
}
