import type { SkillCategory, Project, ExperienceItem, EducationItem, NavLink, Stat } from '@/types'

export const personalInfo = {
  name: 'Saravana Raj P',
  initials: 'SR',
  roles: [
    'AI SaaS Engineer',
    'Team Lead',
    'IT Administrator',
    'Full-Stack Developer',
    'SaaS Architect',
  ],
  location: 'Bengaluru, India',
  email: 'psaravanaraj2609@gmail.com',
  phone: '+91 8531028433',
  linkedin: 'https://www.linkedin.com/in/saravana-raj-462b2612a/',
  cvPath: '/Saravana_Raj.pdf',
  summary:
    'Product-focused SaaS web application developer with 3+ years of experience building scalable web applications using Lovable and Supabase. Strong in database design, secure access control, and multi-tenant SaaS architectures. Experienced team lead with a track record of mentoring developers, coordinating cross-functional delivery, and managing IT infrastructure including network administration, system provisioning, and security compliance.',
}

export const stats: Stat[] = [
  { value: '3+', label: 'Years Experience' },
  { value: '3', label: 'Companies' },
  { value: '2', label: 'Degrees' },
  { value: '6+', label: 'Projects Shipped' },
]

export const skillCategories: SkillCategory[] = [
  {
    category: 'AI Dev Tools',
    icon: 'Bot',
    color: '#6C63FF',
    skills: ['Lovable (AI Development)', 'FlutterFlow', 'Prompt Engineering', 'AI-Assisted Coding'],
  },
  {
    category: 'Backend & Database',
    icon: 'Database',
    color: '#00D4FF',
    skills: ['Supabase (PostgreSQL)', 'Row Level Security (RLS)', 'PostgreSQL Functions', 'Firebase (NoSQL)', 'Authentication & Auth Flows'],
  },
  {
    category: 'Architecture',
    icon: 'Layers',
    color: '#a78bfa',
    skills: ['Multi-tenant SaaS Architecture', 'RBAC Design', 'Org-level Data Isolation', 'Secure Access Control', 'Third-party Integrations'],
  },
  {
    category: 'Leadership',
    icon: 'Users',
    color: '#34d399',
    skills: ['Team Leadership & Mentoring', 'Sprint Planning', 'Code Reviews', 'Cross-functional Collaboration', 'Stakeholder Communication'],
  },
  {
    category: 'Infrastructure & DevOps',
    icon: 'Server',
    color: '#f59e0b',
    skills: ['IT Infrastructure', 'Network Administration', 'System Provisioning', 'Security Compliance', 'Git', 'AWS (Basic)', 'Device Management'],
  },
]

export const projects: Project[] = [
  {
    title: 'Shareholder Management System',
    company: 'Rx100 Ventures',
    description:
      'A SaaS platform to manage shareholder records, equity distribution, and cap table data. Built with Supabase for real-time data sync and RLS-enforced data isolation per organization.',
    tags: ['Supabase', 'Lovable', 'RLS', 'PostgreSQL', 'Multi-tenant'],
    accent: '#6C63FF',
    icon: 'PieChart',
  },
  {
    title: 'Procurement Module',
    company: 'Rx100 Ventures',
    description:
      'Multi-tenant procurement workflow system enabling purchase requests, approvals, and vendor management across isolated organization tenants with role-based access control.',
    tags: ['Lovable', 'Supabase', 'RBAC', 'Multi-tenant', 'Workflow'],
    accent: '#00D4FF',
    icon: 'ShoppingCart',
  },
  {
    title: 'BOM System',
    company: 'Rx100 Ventures',
    description:
      'Bill of Materials management platform for manufacturing and product teams. Supports nested component hierarchies, quantity tracking, and supplier linkage.',
    tags: ['Supabase', 'Lovable', 'PostgreSQL', 'SaaS'],
    accent: '#a78bfa',
    icon: 'GitBranch',
  },
  {
    title: 'Company Management Platform',
    company: 'Rx100 Ventures',
    description:
      'Centralized platform for managing multiple portfolio companies with full RBAC. Features organization-level data isolation, user provisioning, and admin dashboards.',
    tags: ['Lovable', 'Supabase', 'RBAC', 'Multi-tenant', 'Admin'],
    accent: '#34d399',
    icon: 'Building2',
  },
  {
    title: 'Healthcare App',
    company: 'Vishwavaidya Healthcare Pvt Ltd',
    description:
      'Healthcare application with secure multi-role authentication, patient data management, and backend service integrations. Built with a strong focus on data security and compliance.',
    tags: ['Firebase', 'Authentication', 'Healthcare', 'Data Flows'],
    accent: '#f59e0b',
    icon: 'HeartPulse',
  },
  {
    title: 'Freelance MVP Builder',
    company: 'Freelance',
    description:
      'Delivered multiple MVPs and internal tools for early-stage startups. Covered end-to-end: authentication flows, CRUD dashboards, clean UI, and stable backend logic for rapid go-to-market.',
    tags: ['FlutterFlow', 'Firebase', 'Auth', 'CRUD', 'MVP'],
    accent: '#fb7185',
    icon: 'Rocket',
  },
]

export const experiences: ExperienceItem[] = [
  {
    role: 'Web Application AI Developer | Team Lead | IT Admin',
    company: 'Rx100 Ventures Builder Pvt Ltd',
    period: 'Feb 2024 — Present',
    location: 'Bengaluru',
    current: true,
    icon: 'Briefcase',
    color: '#6C63FF',
    bullets: [
      'Building SaaS web applications using Lovable and Supabase',
      'Developed Shareholder Management, Procurement, BOM, and Company Management modules',
      'Implemented Supabase Row Level Security (RLS) and PostgreSQL functions',
      'Designed secure organization-level data isolation across multi-tenant systems',
      'Worked closely with stakeholders to translate business workflows into scalable systems',
      'Leading and mentoring a team of developers, conducting code reviews and sprint planning',
      'Coordinating cross-functional collaboration to ensure timely feature delivery',
      'Managing IT infrastructure including network setup, system provisioning, and user access controls',
    ],
  },
  {
    role: 'Freelance Mobile Application Developer',
    company: 'Self-employed',
    period: 'Jul 2023 — Feb 2024',
    location: 'Remote',
    current: false,
    icon: 'Laptop',
    color: '#00D4FF',
    bullets: [
      'Built MVPs and internal tools for startups from concept to delivery',
      'Implemented authentication, dashboards, and full CRUD workflows',
      'Delivered clean, polished UI paired with stable backend logic',
    ],
  },
  {
    role: 'Application Developer',
    company: 'Vishwavaidya Healthcare Pvt Ltd',
    period: 'Jun 2022 — Jul 2023',
    location: 'Delhi',
    current: false,
    icon: 'HeartPulse',
    color: '#34d399',
    bullets: [
      'Developed healthcare applications with secure user authentication',
      'Integrated backend services and managed application data flows',
      'Collaborated with cross-functional teams for feature delivery',
    ],
  },
]

export const education: EducationItem[] = [
  {
    degree: 'MCA — Master of Computer Applications',
    institution: 'Kongu Engineering College',
    year: '2020',
    icon: 'GraduationCap',
  },
  {
    degree: 'B.Sc — Software Systems',
    institution: 'Kongu Engineering College',
    year: '2018',
    icon: 'BookOpen',
  },
]

export const navLinks: NavLink[] = [
  { label: 'About', href: '#about' },
  { label: 'Skills', href: '#skills' },
  { label: 'Projects', href: '#projects' },
  { label: 'Experience', href: '#experience' },
  { label: 'Contact', href: '#contact' },
]
