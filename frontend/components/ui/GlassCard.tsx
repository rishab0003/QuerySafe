import React from 'react';
import { cn } from '@/lib/utils';

type GlassCardProps = {
  children: React.ReactNode;
  className?: string;
};

export default function GlassCard({ children, className }: GlassCardProps) {
  return (
    <div
      className={cn(
        'bg-white/5 backdrop-blur-lg border border-white/10 rounded-xl shadow-md p-4',
        className,
      )}
    >
      {children}
    </div>
  );
}
