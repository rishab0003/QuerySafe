import React from 'react'
import SectionWrapper from '@/components/ui/SectionWrapper'
import GlassCard from '@/components/ui/GlassCard'
import TagLabel from '@/components/ui/TagLabel'
import Marquee from '@/components/ui/Marquee'
import { motion } from 'framer-motion'
import { fadeUp, stagger } from '@/lib/motion'

// List of partner logo image URLs (placeholder SVG icons from Lucide for demo)
const logos = [
  'https://api.iconify.design/logos/postgresql.svg?size=48',
  'https://api.iconify.design/logos/mysql.svg?size=48',
  'https://api.iconify.design/logos/mongodb.svg?size=48',
  'https://api.iconify.design/logos/google-cloud.svg?size=48',
  'https://api.iconify.design/logos/aws.svg?size=48',
  'https://api.iconify.design/logos/azure.svg?size=48',
]

export default function IntegrationsSection() {
  return (
    <SectionWrapper id="integrations" className="bg-surface-base">
      <TagLabel text="INTEGRATIONS" className="mb-4" />
      <GlassCard className="p-6 bg-white/5 backdrop-blur-lg border border-white/10">
        <motion.div variants={stagger} initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-80px' }}>
          <motion.h2 variants={fadeAll} className="text-4xl font-display font-bold text-center mb-8 text-white">
            Seamless Integrations
          </motion.h2>
          <motion.p variants={fadeUp} className="text-center text-zinc-300 mb-6 max-w-2xl mx-auto">
            Connect to any of your favorite data stores and cloud platforms with zero configuration.
          </motion.p>
          <Marquee className="h-20" pauseOnHover>
            {logos.map((src, i) => (
              <img key={i} src={src} alt="logo" className="h-12 w-auto mx-4 object-contain" />
            ))}
          </Marquee>
        </motion.div>
      </GlassCard>
    </SectionWrapper>
  )
}

// Simple fadeAll variant for heading
const fadeAll = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } },
}
