import React from 'react'

export default function Footer(){
  return (
    <footer className="mt-20 border-t border-[var(--border-subtle)] bg-[var(--bg-surface)]/80">
      <div className="mx-auto flex max-w-6xl flex-col gap-8 px-6 py-8 sm:flex-row sm:items-start sm:justify-between">
        <div className="max-w-sm">
          <div className="font-display text-lg">QuerySafe</div>
          <div className="mt-1 text-xs text-[var(--text-muted)]">Built in 3 days. Secured by design. Powered by AI.</div>
        </div>
        <div className="flex gap-8">
          <div>
            <div className="font-medium">Product</div>
            <div className="mt-2 text-xs text-[var(--text-muted)]">Docs · Pricing · Changelog</div>
          </div>
          <div>
            <div className="font-medium">Company</div>
            <div className="mt-2 text-xs text-[var(--text-muted)]">About · Careers · Contact</div>
          </div>
        </div>
        <div className="text-xs text-[var(--text-muted)]">© {new Date().getFullYear()} QuerySafe</div>
      </div>
    </footer>
  )
}
