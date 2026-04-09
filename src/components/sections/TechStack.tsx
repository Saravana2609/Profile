import { motion } from 'framer-motion'
import {
  SiReact, SiTypescript, SiJavascript, SiHtml5, SiCss,
  SiTailwindcss, SiFramer, SiVite, SiPython,
  SiSupabase, SiPostgresql, SiMongodb, SiSparkar, SiAnthropic,
} from 'react-icons/si'
import type { IconType } from 'react-icons'
import SectionTitle from '@/components/ui/SectionTitle'

interface TechItem {
  label: string
  Icon: IconType
  color: string
}

const items: TechItem[] = [
  { label: 'React',           Icon: SiReact,      color: '#61DAFB' },
  { label: 'TypeScript',      Icon: SiTypescript,  color: '#3178C6' },
  { label: 'JavaScript',      Icon: SiJavascript,  color: '#F7DF1E' },
  { label: 'HTML',            Icon: SiHtml5,       color: '#E34F26' },
  { label: 'CSS',             Icon: SiCss,         color: '#1572B6' },
  { label: 'Tailwind CSS',    Icon: SiTailwindcss, color: '#06B6D4' },
  { label: 'Framer Motion',   Icon: SiFramer,      color: '#AA44FF' },
  { label: 'Vite',            Icon: SiVite,        color: '#646CFF' },
  { label: 'Python',          Icon: SiPython,      color: '#3776AB' },
  { label: 'Supabase',        Icon: SiSupabase,    color: '#3ECF8E' },
  { label: 'SQL',             Icon: SiPostgresql,  color: '#336791' },
  { label: 'NoSQL',           Icon: SiMongodb,     color: '#47A248' },
  { label: 'Lovable',         Icon: SiSparkar,     color: '#FF4F64' },
  { label: 'Claude in VS Code', Icon: SiAnthropic, color: '#D97757' },
]

const doubled = [...items, ...items]

export default function TechStack() {
  return (
    <section id="techstack" className="py-16 px-6">
      <div className="max-w-6xl mx-auto">
        <SectionTitle title="Tech Stacks" subtitle="Technologies I build with" />
      </div>

      <div
        className="relative overflow-hidden"
        style={{
          maskImage: 'linear-gradient(to right, transparent, black 12%, black 88%, transparent)',
          WebkitMaskImage: 'linear-gradient(to right, transparent, black 12%, black 88%, transparent)',
        }}
      >
        <motion.div
          className="flex gap-4 w-max"
          animate={{ x: ['0%', '-50%'] }}
          transition={{ duration: 28, repeat: Infinity, ease: 'linear' }}
        >
          {doubled.map(({ label, Icon, color }, i) => (
            <span
              key={i}
              className="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium whitespace-nowrap"
              style={{
                color,
                border: `1px solid ${color}50`,
                background: `${color}18`,
              }}
            >
              <Icon size={16} />
              {label}
            </span>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
