import React from 'react';
import { cn } from '@/lib/utils';

type TagLabelProps = {
  text: string;
  className?: string;
};

export default function TagLabel({ text, className }: TagLabelProps) {
  return (
    <span
      className={cn(
        'font-mono text-xs uppercase text-gray-500 bg-white/5 px-2 py-1 rounded',
        className,
      )}
    >
      {text}
    </span>
  );
}
