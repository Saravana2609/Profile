import { motion } from 'framer-motion'
import { MapPin, Mail, Phone, GraduationCap, BookOpen } from 'lucide-react'
import { personalInfo, stats, education } from '@/data/portfolio-data'
import SectionTitle from '@/components/ui/SectionTitle'
import GlassCard from '@/components/ui/GlassCard'

const iconComponents = { GraduationCap, BookOpen }

export default function About() {
  return (
    <section id="about" className="py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <SectionTitle
          title="About Me"
          subtitle="A little about who I am and what I do"
        />

        <div className="grid md:grid-cols-2 gap-10 items-start">
          {/* Left: Bio */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="flex flex-col gap-6"
          >
            <div className="border-l-4 border-primary pl-5">
              <p className="text-[#e2e8f0] leading-relaxed">{personalInfo.summary}</p>
            </div>

            {/* Contact info */}
            <div className="flex flex-col gap-3">
              {[
                { icon: MapPin, text: personalInfo.location },
                { icon: Mail, text: personalInfo.email },
                { icon: Phone, text: personalInfo.phone },
              ].map(({ icon: Icon, text }) => (
                <div key={text} className="flex items-center gap-3 text-textMuted text-sm">
                  <Icon size={16} className="text-primary flex-shrink-0" />
                  <span>{text}</span>
                </div>
              ))}
            </div>

            {/* Education */}
            <div>
              <h3 className="text-sm font-semibold text-textMuted uppercase tracking-widest mb-3">
                Education
              </h3>
              <div className="flex flex-col gap-3">
                {education.map((edu) => {
                  const Icon = iconComponents[edu.icon as keyof typeof iconComponents]
                  return (
                    <div key={edu.degree} className="flex items-start gap-3">
                      <div className="mt-0.5 p-1.5 rounded-lg bg-primary/10">
                        <Icon size={14} className="text-primary" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-[#e2e8f0]">{edu.degree}</p>
                        <p className="text-xs text-textMuted">{edu.institution} · {edu.year}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </motion.div>

          {/* Right: Stats */}
          <div className="flex flex-col gap-4">
            <div className="grid grid-cols-2 gap-4">
              {stats.map((stat, i) => (
                <GlassCard key={stat.label} delay={i * 0.1} className="text-center">
                  <p className="text-4xl font-extrabold text-gradient mb-1">{stat.value}</p>
                  <p className="text-textMuted text-sm">{stat.label}</p>
                </GlassCard>
              ))}
            </div>

            {/* Trait badges */}
            <div className="flex flex-wrap gap-2 mt-2">
              {['Team Player', 'Problem Solver', 'Agile', 'Detail-oriented', 'Fast Learner', 'Mentor'].map((trait) => (
                <span
                  key={trait}
                  className="px-3 py-1.5 rounded-full text-xs font-medium glass text-textMuted border-white/10"
                >
                  {trait}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
