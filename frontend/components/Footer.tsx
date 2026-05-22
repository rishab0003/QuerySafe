import React from 'react'

export default function Footer(){
  return (
    <footer className="bg-[#07090d] border-t border-[--border-subtle] mt-20">
      <div className="max-w-6xl mx-auto px-6 py-8 flex items-start justify-between gap-6">
        <div>
          <div className="font-display text-lg">QuerySafe</div>
          <div className="text-xs text-[--text-muted] mt-1">Built in 3 days. Secured by design. Powered by AI.</div>
        </div>
        <div className="flex gap-8">
          <div>
            <div className="font-medium">Product</div>
            <div className="text-xs text-[--text-muted] mt-2">Docs · Pricing · Changelog</div>
          </div>
          <div>
            <div className="font-medium">Company</div>
            <div className="text-xs text-[--text-muted] mt-2">About · Careers · Contact</div>
          </div>
        </div>
        <div className="text-xs text-[--text-muted]">© {new Date().getFullYear()} QuerySafe</div>
      </div>
    </footer>
  )
}
