import { useState, useEffect } from 'react'

export function useTypingEffect(
  titles: string[],
  typingSpeed = 80,
  deletingSpeed = 40,
  pauseDuration = 2000
) {
  const [displayText, setDisplayText] = useState('')
  const [titleIndex, setTitleIndex] = useState(0)
  const [isDeleting, setIsDeleting] = useState(false)
  const [isPausing, setIsPausing] = useState(false)

  useEffect(() => {
    if (isPausing) return

    const current = titles[titleIndex]

    const timeout = setTimeout(() => {
      if (!isDeleting) {
        const next = current.slice(0, displayText.length + 1)
        setDisplayText(next)
        if (next === current) {
          setIsPausing(true)
          setTimeout(() => {
            setIsPausing(false)
            setIsDeleting(true)
          }, pauseDuration)
        }
      } else {
        const next = current.slice(0, displayText.length - 1)
        setDisplayText(next)
        if (next === '') {
          setIsDeleting(false)
          setTitleIndex((prev) => (prev + 1) % titles.length)
        }
      }
    }, isDeleting ? deletingSpeed : typingSpeed)

    return () => clearTimeout(timeout)
  }, [displayText, isDeleting, isPausing, titleIndex, titles, typingSpeed, deletingSpeed, pauseDuration])

  return { displayText }
}
