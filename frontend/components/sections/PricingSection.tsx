import React from 'react'
import SectionWrapper from '@/components/ui/SectionWrapper'
import GlowCard from '@/components/ui/GlowCard'
import { motion } from 'framer-motion'
import { fadeUp, stagger } from '@/lib/motion'
import { Check } from 'lucide-react'

const plans = [
  {
    name: 'Free',
    price: '$0',
    period: '/mo',
    features: ['Up to 5 queries/day', 'Basic AI model', 'Community support'],
    highlight: false,
  },
  {
    name: 'Pro',
    price: '$49',
    period: '/mo',
    features: ['Unlimited queries', 'Premium AI model', 'Priority support', 'Custom integrations'],
    highlight: true,
  },
  {
    name: 'Enterprise',
    price: 'Contact us',
    period: '',
    features: ['Dedicated instance', 'SLAs', 'On‑premise deployment', 'Dedicated success manager'],
    highlight: false,
  },
]

export default function PricingSection() {
  return (
    <SectionWrapper id="pricing" className="bg-surface-base">
      <motion.div variants={stagger} initial="hidden" whileInView="visible" viewport={{ once: true, margin: '-80px' }}>
        <motion.h2 variants={fadeUp} className="text-4xl font-display font-bold text-center mb-8 text-white">
          Flexible Pricing
        </motion.h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {plans.map((plan, i) => (
            <GlowCard
              key={i}
              className={`flex flex-col p-6 ${plan.highlight ? 'border-2 border-violet-500/60' : ''}`}
            >
              <h3 className="text-xl font-display font-semibold text-white mb-2 text-center">
                {plan.name}
              </h3>
              <p className="text-3xl font-bold text-center text-white mb-4">
                {plan.price}<span className="text-base font-medium text-zinc-300">{plan.period}</span>
              </p>
              <ul className="flex-1 space-y-2 mb-6">
                {plan.features.map((f, idx) => (
                  <li key={idx} className="flex items-center gap-2 text-zinc-300 text-sm">
                    <Check className="h-4 w-4 text-white" /> {f}
                  </li>
                ))}
              </ul>
              <button className="qs-btn-primary w-full">{plan.name === 'Enterprise' ? 'Contact Sales' : 'Get Started'}</button>
            </GlowCard>
          ))}
        </div>
      </motion.div>
    </SectionWrapper>
  )
}
