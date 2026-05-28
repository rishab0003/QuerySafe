import Link from 'next/link'
import { Github, Twitter, Linkedin } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="bg-surface-base text-zinc-400 border-t border-white/5 py-12">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 px-4 sm:px-6 lg:px-8">
        {/* Logo & tagline */}
        <div className="flex flex-col space-y-4">
          <Link href="/" className="flex items-center space-x-2">
            <img src="/logo.svg" alt="QuerySafe" className="h-8 w-8" />
            <span className="text-xl font-display font-bold text-white">QuerySafe</span>
          </Link>
          <p className="text-sm max-w-xs">AI‑native SaaS for secure natural‑language database queries.</p>
          <div className="flex space-x-4 mt-2">
            <a href="https://github.com/yourorg/querysafe" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
              <Github className="h-5 w-5 hover:text-white transition-colors" />
            </a>
            <a href="https://twitter.com/yourorg" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
              <Twitter className="h-5 w-5 hover:text-white transition-colors" />
            </a>
            <a href="https://linkedin.com/company/yourorg" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
              <Linkedin className="h-5 w-5 hover:text-white transition-colors" />
            </a>
          </div>
        </div>
        {/* Product links */}
        <nav className="flex flex-col space-y-2">
          <h4 className="text-sm font-medium text-zinc-300 mb-2">Product</h4>
          <Link href="#features" className="hover:text-white transition-colors">Features</Link>
          <Link href="#security" className="hover:text-white transition-colors">Security</Link>
          <Link href="#integrations" className="hover:text-white transition-colors">Integrations</Link>
          <Link href="#pricing" className="hover:text-white transition-colors">Pricing</Link>
          <Link href="#changelog" className="hover:text-white transition-colors">Changelog</Link>
        </nav>
        {/* Resources links */}
        <nav className="flex flex-col space-y-2">
          <h4 className="text-sm font-medium text-zinc-300 mb-2">Resources</h4>
          <Link href="/docs" className="hover:text-white transition-colors">Docs</Link>
          <Link href="/api" className="hover:text-white transition-colors">API Reference</Link>
          <Link href="/blog" className="hover:text-white transition-colors">Blog</Link>
          <Link href="/case-studies" className="hover:text-white transition-colors">Case Studies</Link>
          <Link href="/status" className="hover:text-white transition-colors">Status</Link>
        </nav>
        {/* Company links */}
        <nav className="flex flex-col space-y-2">
          <h4 className="text-sm font-medium text-zinc-300 mb-2">Company</h4>
          <Link href="/about" className="hover:text-white transition-colors">About</Link>
          <Link href="/careers" className="hover:text-white transition-colors">Careers</Link>
          <Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
          <Link href="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
          <Link href="/contact" className="hover:text-white transition-colors">Contact</Link>
        </nav>
      </div>
      <div className="border-t border-white/5 mt-8 pt-4 text-center text-xs text-zinc-600">
        © 2026 QuerySafe · MIT License · Built with ❤️ in 3 days
      </div>
    </footer>
  )
}
