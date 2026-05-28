import React from 'react';
import Link from 'next/link';
import { ArrowRight, Shield } from 'lucide-react';
import SectionWrapper from '@/components/ui/SectionWrapper';
import GlassCard from '@/components/ui/GlassCard';

export default function FinalCTA() {
  return (
    <SectionWrapper id="cta" className="relative overflow-hidden py-24">
      {/* Background glow effects */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] rounded-full bg-jade/[0.08] blur-[100px] animate-glow-pulse" />
      </div>

      <div className="max-w-4xl mx-auto text-center relative z-10 px-4">
        <GlassCard className="p-12 md:p-16 bg-gradient-to-b from-white/[0.03] to-white/[0.01] border border-[var(--border-subtle)] rounded-3xl shadow-glow relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-jade/30 to-transparent" />
          
          <div className="inline-flex p-3 rounded-2xl bg-jade/10 border border-jade/20 text-jade mb-6">
            <Shield size={24} />
          </div>

          <h2 className="text-3xl md:text-5xl font-display font-bold text-[--text-primary] tracking-tight mb-4">
            Ready to secure your database access?
          </h2>
          
          <p className="text-base text-[--text-muted] max-w-xl mx-auto mb-8 leading-relaxed">
            Deploy QuerySafe in minutes and give your team secure, audit-ready natural language database access. Enforce read-only access with zero configuration.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              href="/auth/register"
              className="qs-btn-primary rounded-xl px-8 py-3.5 text-base font-semibold shadow-glow w-full sm:w-auto"
            >
              Get Started for Free
            </Link>
            <Link
              href="/auth/login"
              className="qs-btn-ghost rounded-xl px-8 py-3.5 text-base font-semibold border border-[var(--border-subtle)] hover:bg-black/5 dark:hover:bg-white/5 transition-all w-full sm:w-auto flex items-center justify-center gap-2"
            >
              Sign In to Workspace
              <ArrowRight size={16} />
            </Link>
          </div>
        </GlassCard>
      </div>
    </SectionWrapper>
  );
}
