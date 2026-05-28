import React from 'react'
import SectionWrapper from '@/components/ui/SectionWrapper'
import GlowCard from '@/components/ui/GlowCard'
import { motion } from 'framer-motion'
import { fadeUp, stagger } from '@/lib/motion'
import { User, MessageSquare } from 'lucide-react'

const testimonials = [
  {
    name: 'Riya Patel',
    role: 'Head of Data – FinTech Corp',
    avatar: 'https://api.dicebear.com/6.x/identicon/svg?seed=riya',
    quote: "QuerySafe turned our data lake into an instant‑answer engine. No more hand‑crafted SQL!",
  },
  {
    name: 'Liam O’Connor',
    role: 'Security Engineer – HealthCo',
    avatar: 'https://api.dicebear.com/6.x/identicon/svg?seed=liam',
    quote: "The built‑in read‑only enforcement gives me peace of mind while developers stay productive.",
  },
  {
    name: 'Sofia García',
    role: 'Product Lead – Retailify',
    avatar: 'https://api.dicebear.com/6.x/identicon/svg?seed=sofia',
    quote: "Our analysts love the natural‑language UI. The AI explanations are crystal clear.",
  },
]

export default function TestimonialsSection() {
  return (
    <SectionWrapper id="testimonials" className="bg-surface-base">
      <motion.div variants={stagger} initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-80px' }}>
        <motion.h2 variants={fadeUp} className="text-4xl font-display font-bold text-center mb-8 text-white">
          What Our Users Say
        </motion.h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {testimonials.map((t, i) => (
            <GlowCard key={i} className="p-6 flex flex-col h-full">
              <div className="flex items-center gap-3 mb-4">
                <img src={t.avatar} alt={t.name} className="h-10 w-10 rounded-full" />
                <div>
                  <p className="font-display text-sm font-semibold text-white">{t.name}</p>
                  <p className="text-xs text-zinc-400">{t.role}</p>
                </div>
              </div>
              <p className="flex-1 text-zinc-300 italic text-sm">
                <MessageSquare className="inline mr-2 h-4 w-4 text-white" />{t.quote}
              </p>
            </GlowCard>
          ))}
        </div>
      </motion.div>
    </SectionWrapper>
  )
}
