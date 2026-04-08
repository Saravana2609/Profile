import { motion } from 'framer-motion'
import type { ReactNode } from 'react'

interface GlassCardProps {
  children: ReactNode
  className?: string
  hoverEffect?: boolean
  delay?: number
}

export default function GlassCard({
  children,
  className = '',
  hoverEffect = true,
  delay = 0,
}: GlassCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.5, delay }}
      whileHover={hoverEffect ? { y: -4, scale: 1.01 } : undefined}
      className={`glass glass-hover rounded-xl p-6 ${className}`}
    >
      {children}
    </motion.div>
  )
}
