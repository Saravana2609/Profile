export interface NavLink {
  label: string
  href: string
}

export interface Stat {
  value: string
  label: string
}

export interface SkillCategory {
  category: string
  icon: string
  color: string
  skills: string[]
}

export interface Project {
  title: string
  company: string
  description: string
  tags: string[]
  accent: string
  icon: string
}

export interface ExperienceItem {
  role: string
  company: string
  period: string
  location: string
  current: boolean
  icon: string
  color: string
  bullets: string[]
}

export interface EducationItem {
  degree: string
  institution: string
  year: string
  icon: string
}

export type FormStatus = 'idle' | 'sending' | 'success' | 'error'
