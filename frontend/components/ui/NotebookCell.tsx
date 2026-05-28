import React from 'react'
import { cn } from '@/lib/utils'

interface NotebookCellProps {
  index: number
  type: 'code' | 'sql' | 'result'
  content: string
  isRunning?: boolean
  output?: React.ReactNode
  className?: string
}

export default function NotebookCell({ index, type, content, isRunning = false, output, className }: NotebookCellProps) {
  const baseBorder = type === 'result' ? 'border-violet-500/20 bg-violet-950/20' : 'border-white/8 bg-white/3'
  const title = type === 'code' ? 'Code' : type === 'sql' ? 'SQL' : 'Result'
  return (
    <div className={cn('flex gap-3 mb-3 group', className)}>
      {/* Index */}
      <div className="flex-shrink-0 w-8 text-right text-xs text-zinc-600 pt-3 font-mono">[{index}]:</div>
      {/* Cell */}
      <div className={cn('flex-1 rounded-lg border p-3', baseBorder)}>
        <div className="font-mono text-sm leading-relaxed">
          {type === 'code' && <span className="text-cyan-400">{content}</span>}
          {type === 'sql' && <span className="text-green-300">{content}</span>}
          {type === 'result' && <span className="text-zinc-300">{content}</span>}
        </div>
        {output && (
          <div className="mt-3 pt-3 border-t border-white/5 text-sm text-zinc-300">
            {output}
          </div>
        )}
      </div>
      {/* Running indicator */}
      {isRunning && <div className="w-2 h-2 rounded-full bg-violet-500 animate-glow-pulse mt-4" />}
    </div>
  )
}
