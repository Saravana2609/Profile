import { useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Mail, Phone, MapPin, Send, CheckCircle2 } from 'lucide-react'
import LinkedinIcon from '@/components/ui/LinkedinIcon'
import { personalInfo } from '@/data/portfolio-data'
import { sendContactEmail } from '@/utils/emailjs'
import SectionTitle from '@/components/ui/SectionTitle'
import type { FormStatus } from '@/types'

export default function Contact() {
  const formRef = useRef<HTMLFormElement>(null)
  const [status, setStatus] = useState<FormStatus>('idle')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!formRef.current) return

    setStatus('sending')
    try {
      await sendContactEmail(formRef.current)
      setStatus('success')
      formRef.current.reset()
      setTimeout(() => setStatus('idle'), 5000)
    } catch {
      setStatus('error')
      setTimeout(() => setStatus('idle'), 4000)
    }
  }

  const inputClass =
    'w-full px-4 py-3 rounded-xl glass text-[#e2e8f0] placeholder-textMuted text-sm outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/40 transition-all border border-white/10 bg-transparent'

  return (
    <section id="contact" className="py-24 px-6">
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse 60% 40% at 50% 90%, rgba(108,99,255,0.08), transparent)',
        }}
      />
      <div className="max-w-5xl mx-auto">
        <SectionTitle title="Get In Touch" subtitle="Have a project or opportunity? I'd love to hear from you." />

        <div className="grid md:grid-cols-2 gap-10">
          {/* Left info panel */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="flex flex-col gap-6"
          >
            <div>
              <h3 className="text-2xl font-bold text-[#e2e8f0] mb-2">Let's work together</h3>
              <p className="text-textMuted leading-relaxed">
                Whether you need a SaaS platform, a scalable backend, or a technical team lead — I'm here to help turn ideas into reality.
              </p>
            </div>

            <div className="flex flex-col gap-4">
              {[
                { icon: Mail, text: personalInfo.email, href: `mailto:${personalInfo.email}` },
                { icon: Phone, text: personalInfo.phone, href: `tel:${personalInfo.phone}` },
                { icon: MapPin, text: personalInfo.location, href: null },
              ].map(({ icon: Icon, text, href }) => (
                <div key={text} className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-primary/10">
                    <Icon size={16} className="text-primary" />
                  </div>
                  {href ? (
                    <a href={href} className="text-textMuted text-sm hover:text-white transition-colors">
                      {text}
                    </a>
                  ) : (
                    <span className="text-textMuted text-sm">{text}</span>
                  )}
                </div>
              ))}
            </div>

            <a
              href={personalInfo.linkedin}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 glass glass-hover rounded-xl px-5 py-3 w-fit"
            >
              <LinkedinIcon size={18} className="text-primary" />
              <span className="text-sm text-textMuted">Connect on LinkedIn</span>
            </a>
          </motion.div>

          {/* Right form */}
          <motion.div
            initial={{ opacity: 0, x: 30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <form ref={formRef} onSubmit={handleSubmit} className="glass rounded-2xl p-8 flex flex-col gap-4">
              <input type="hidden" name="to_name" value="Saravana Raj" />

              <div>
                <label className="text-xs font-medium text-textMuted uppercase tracking-widest mb-1.5 block">
                  Name
                </label>
                <input
                  type="text"
                  name="from_name"
                  required
                  placeholder="Your name"
                  className={inputClass}
                />
              </div>

              <div>
                <label className="text-xs font-medium text-textMuted uppercase tracking-widest mb-1.5 block">
                  Email
                </label>
                <input
                  type="email"
                  name="from_email"
                  required
                  placeholder="your@email.com"
                  className={inputClass}
                />
              </div>

              <div>
                <label className="text-xs font-medium text-textMuted uppercase tracking-widest mb-1.5 block">
                  Message
                </label>
                <textarea
                  name="message"
                  required
                  rows={5}
                  placeholder="Tell me about your project..."
                  className={`${inputClass} resize-none`}
                />
              </div>

              <button
                type="submit"
                disabled={status === 'sending'}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-primary to-secondary hover:opacity-90 disabled:opacity-60 transition-all"
              >
                {status === 'sending' ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                    </svg>
                    Sending...
                  </>
                ) : status === 'success' ? (
                  <>
                    <CheckCircle2 size={18} />
                    Message Sent!
                  </>
                ) : (
                  <>
                    <Send size={16} />
                    Send Message
                  </>
                )}
              </button>

              {status === 'error' && (
                <p className="text-red-400 text-sm text-center">
                  Something went wrong. Please try again or email directly.
                </p>
              )}

              {status === 'success' && (
                <p className="text-emerald-400 text-sm text-center">
                  Thanks! I'll get back to you soon.
                </p>
              )}
            </form>
          </motion.div>
        </div>
      </div>
    </section>
  )
}
