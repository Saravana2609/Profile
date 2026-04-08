import { motion } from 'framer-motion'
import { Briefcase, Laptop, HeartPulse, CheckCircle2, Calendar, MapPin } from 'lucide-react'
import { experiences } from '@/data/portfolio-data'
import SectionTitle from '@/components/ui/SectionTitle'
import type { LucideProps } from 'lucide-react'
import type { ComponentType } from 'react'

const iconMap: Record<string, ComponentType<LucideProps>> = {
  Briefcase, Laptop, HeartPulse,
}

export default function Experience() {
  return (
    <section id="experience" className="py-24 px-6">
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 50% 40% at 90% 50%, rgba(0,212,255,0.05), transparent)',
        }}
      />
      <div className="max-w-4xl mx-auto">
        <SectionTitle title="Experience" subtitle="My professional journey so far" />

        <div className="relative">
          {/* Vertical line */}
          <div
            className="absolute left-5 top-0 bottom-0 w-0.5"
            style={{
              background: 'linear-gradient(to bottom, #6C63FF, #00D4FF, transparent)',
            }}
          />

          <div className="flex flex-col gap-10 pl-16">
            {experiences.map((exp, i) => {
              const Icon = iconMap[exp.icon]
              return (
                <motion.div
                  key={exp.company + exp.period}
                  initial={{ opacity: 0, x: -30 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: i * 0.15 }}
                  className="relative"
                >
                  {/* Connector circle */}
                  <div
                    className="absolute -left-11 top-5 w-10 h-10 rounded-full flex items-center justify-center glass"
                    style={{ border: `2px solid ${exp.color}` }}
                  >
                    {Icon && <Icon size={16} style={{ color: exp.color }} />}
                  </div>

                  {/* Card */}
                  <div className="glass glass-hover rounded-xl p-6">
                    {/* Header */}
                    <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2 mb-4">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-bold text-[#e2e8f0] text-base leading-snug">{exp.role}</h3>
                          {exp.current && (
                            <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                              Current
                            </span>
                          )}
                        </div>
                        <p className="font-medium mt-0.5" style={{ color: exp.color }}>
                          {exp.company}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1 text-xs text-textMuted sm:text-right">
                        <span className="flex items-center gap-1 sm:justify-end">
                          <Calendar size={11} />
                          {exp.period}
                        </span>
                        <span className="flex items-center gap-1 sm:justify-end">
                          <MapPin size={11} />
                          {exp.location}
                        </span>
                      </div>
                    </div>

                    {/* Bullets */}
                    <ul className="flex flex-col gap-2">
                      {exp.bullets.map((bullet) => (
                        <li key={bullet} className="flex items-start gap-2.5 text-sm text-textMuted">
                          <CheckCircle2
                            size={14}
                            className="flex-shrink-0 mt-0.5"
                            style={{ color: exp.color }}
                          />
                          <span>{bullet}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </motion.div>
              )
            })}
          </div>
        </div>
      </div>
    </section>
  )
}
