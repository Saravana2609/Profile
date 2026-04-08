import { motion } from 'framer-motion'
import {
  PieChart, ShoppingCart, GitBranch, Building2, HeartPulse, Rocket,
} from 'lucide-react'
import { projects } from '@/data/portfolio-data'
import SectionTitle from '@/components/ui/SectionTitle'
import type { LucideProps } from 'lucide-react'
import type { ComponentType } from 'react'

const iconMap: Record<string, ComponentType<LucideProps>> = {
  PieChart, ShoppingCart, GitBranch, Building2, HeartPulse, Rocket,
}

export default function Projects() {
  return (
    <section id="projects" className="py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <SectionTitle
          title="Projects"
          subtitle="A selection of work I've built across SaaS, healthcare, and startup domains"
        />

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project, i) => {
            const Icon = iconMap[project.icon]
            return (
              <motion.div
                key={project.title}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-40px' }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
                whileHover={{ y: -6 }}
                className="glass rounded-xl flex flex-col overflow-hidden transition-all duration-300 group"
                style={{
                  borderColor: `${project.accent}20`,
                }}
                onMouseEnter={(e) => {
                  ;(e.currentTarget as HTMLDivElement).style.borderColor = `${project.accent}50`
                  ;(e.currentTarget as HTMLDivElement).style.boxShadow = `0 8px 32px ${project.accent}20`
                }}
                onMouseLeave={(e) => {
                  ;(e.currentTarget as HTMLDivElement).style.borderColor = `${project.accent}20`
                  ;(e.currentTarget as HTMLDivElement).style.boxShadow = 'none'
                }}
              >
                {/* Card body */}
                <div className="p-6 flex flex-col gap-3 flex-1">
                  {/* Top row */}
                  <div className="flex items-start justify-between">
                    <div
                      className="p-2.5 rounded-lg"
                      style={{ background: `${project.accent}20` }}
                    >
                      {Icon && <Icon size={22} style={{ color: project.accent }} />}
                    </div>
                    <span className="text-xs text-textMuted">{project.company}</span>
                  </div>

                  {/* Title */}
                  <h3 className="font-bold text-[#e2e8f0] text-base leading-snug">{project.title}</h3>

                  {/* Description */}
                  <p className="text-textMuted text-sm leading-relaxed flex-1 line-clamp-3">
                    {project.description}
                  </p>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-1.5 pt-1">
                    {project.tags.map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-0.5 rounded text-xs bg-white/5 text-textMuted"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Bottom accent line */}
                <div
                  className="h-0.5 w-full"
                  style={{
                    background: `linear-gradient(to right, ${project.accent}, transparent)`,
                  }}
                />
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
