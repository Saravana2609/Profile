import { motion } from 'framer-motion'
import { Bot, Database, Layers, Users, Server } from 'lucide-react'
import { skillCategories } from '@/data/portfolio-data'
import SectionTitle from '@/components/ui/SectionTitle'
import type { LucideProps } from 'lucide-react'
import type { ComponentType } from 'react'

const iconMap: Record<string, ComponentType<LucideProps>> = {
  Bot, Database, Layers, Users, Server,
}

export default function Skills() {
  return (
    <section id="skills" className="py-24 px-6">
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 60% 40% at 10% 50%, rgba(108,99,255,0.06), transparent)',
        }}
      />
      <div className="max-w-6xl mx-auto">
        <SectionTitle
          title="Skills"
          subtitle="Technologies and tools I work with every day"
        />

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {skillCategories.map((cat, i) => {
            const Icon = iconMap[cat.icon]
            return (
              <motion.div
                key={cat.category}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                whileHover={{ y: -4, scale: 1.01 }}
                className="glass glass-hover rounded-xl p-6 flex flex-col gap-4"
                style={{ borderTop: `2px solid ${cat.color}` }}
              >
                {/* Header */}
                <div className="flex items-center gap-3">
                  <div
                    className="p-2 rounded-lg"
                    style={{ background: `${cat.color}20` }}
                  >
                    {Icon && <Icon size={20} style={{ color: cat.color }} />}
                  </div>
                  <h3 className="font-semibold text-[#e2e8f0]">{cat.category}</h3>
                </div>

                {/* Skill pills */}
                <div className="flex flex-wrap gap-2">
                  {cat.skills.map((skill) => (
                    <span
                      key={skill}
                      className="px-2.5 py-1 rounded-full text-xs font-medium"
                      style={{
                        background: `${cat.color}18`,
                        color: cat.color,
                        border: `1px solid ${cat.color}30`,
                      }}
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </motion.div>
            )
          })}
        </div>
      </div>
    </section>
  )
}
