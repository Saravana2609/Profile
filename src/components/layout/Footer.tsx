import { Mail } from 'lucide-react'
import LinkedinIcon from '@/components/ui/LinkedinIcon'
import { personalInfo } from '@/data/portfolio-data'

export default function Footer() {
  return (
    <footer className="border-t border-white/5 py-8 px-6">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-textMuted">
        <span className="font-semibold text-gradient">{personalInfo.name}</span>

        <span>© {new Date().getFullYear()} {personalInfo.name}. All rights reserved.</span>

        <div className="flex items-center gap-4">
          <a
            href={`mailto:${personalInfo.email}`}
            className="hover:text-primary transition-colors"
            aria-label="Email"
          >
            <Mail size={18} />
          </a>
          <a
            href={personalInfo.linkedin}
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-primary transition-colors"
            aria-label="LinkedIn"
          >
            <LinkedinIcon size={18} />
          </a>
        </div>
      </div>
      <p className="text-center text-xs text-white/20 mt-4">Built with React · Vite · Tailwind CSS · Framer Motion</p>
    </footer>
  )
}
