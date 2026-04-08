import { motion } from 'framer-motion'
import { Download, ChevronDown } from 'lucide-react'
import { personalInfo } from '@/data/portfolio-data'
import { useTypingEffect } from '@/hooks/useTypingEffect'
import ParticleBackground from '@/components/ui/ParticleBackground'

const fadeUp = (delay: number) => ({
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, delay },
})

export default function Hero() {
  const { displayText } = useTypingEffect(personalInfo.roles)

  const handleContactClick = () => {
    document.getElementById('contact')?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <section className="relative min-h-screen flex flex-col items-center justify-center text-center px-6 overflow-hidden">
      {/* Background layers */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            'radial-gradient(ellipse 80% 50% at 50% 0%, rgba(108,99,255,0.22), transparent), radial-gradient(ellipse 40% 30% at 80% 60%, rgba(0,212,255,0.1), transparent)',
        }}
      />
      <ParticleBackground />

      {/* Content */}
      <div className="relative z-10 max-w-3xl mx-auto flex flex-col items-center gap-6">
        {/* Availability badge */}
        <motion.div {...fadeUp(0)} className="flex items-center gap-2 glass rounded-full px-4 py-2 text-sm">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500" />
          </span>
          <span className="text-textMuted">Available for opportunities</span>
        </motion.div>

        {/* SR Avatar */}
        <motion.div {...fadeUp(0.1)} className="relative">
          <motion.div
            animate={{ y: [0, -12, 0] }}
            transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
            className="relative"
          >
            {/* Outer glow ring */}
            <motion.div
              animate={{ scale: [1, 1.08, 1], opacity: [0.4, 0.7, 0.4] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
              className="absolute inset-0 rounded-full border-2 border-primary/40 scale-110"
            />
            {/* Avatar circle */}
            <div
              className="w-32 h-32 md:w-36 md:h-36 rounded-full flex items-center justify-center text-white font-bold text-4xl md:text-5xl glow-border"
              style={{
                background: 'linear-gradient(135deg, #6C63FF, #00D4FF)',
              }}
            >
              {personalInfo.initials}
            </div>
          </motion.div>
        </motion.div>

        {/* Name */}
        <motion.h1
          {...fadeUp(0.2)}
          className="text-5xl md:text-7xl font-extrabold leading-tight"
        >
          <span className="text-gradient">{personalInfo.name}</span>
        </motion.h1>

        {/* Typing effect */}
        <motion.div {...fadeUp(0.3)} className="h-10 flex items-center justify-center">
          <p className="text-xl md:text-2xl text-textMuted">
            I am a{' '}
            <span className="text-primary font-mono font-semibold">{displayText}</span>
            <span className="animate-blink text-primary font-mono ml-0.5">|</span>
          </p>
        </motion.div>

        {/* Summary */}
        <motion.p
          {...fadeUp(0.4)}
          className="text-textMuted text-base md:text-lg max-w-2xl leading-relaxed"
        >
          {personalInfo.summary.slice(0, 160)}...
        </motion.p>

        {/* CTA Buttons */}
        <motion.div {...fadeUp(0.5)} className="flex flex-wrap gap-4 justify-center">
          <a
            href={personalInfo.cvPath}
            download
            className="flex items-center gap-2 px-6 py-3 rounded-xl border border-primary/60 text-primary font-semibold hover:bg-primary/10 transition-all duration-200"
          >
            <Download size={18} />
            Download CV
          </a>
          <button
            onClick={handleContactClick}
            className="flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition-opacity duration-200"
          >
            Contact Me
          </button>
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        {...fadeUp(0.8)}
        className="absolute bottom-8 left-1/2 -translate-x-1/2"
      >
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <ChevronDown className="text-textMuted" size={28} />
        </motion.div>
      </motion.div>
    </section>
  )
}
