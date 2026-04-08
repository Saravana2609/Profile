import emailjs from '@emailjs/browser'

export const sendContactEmail = (formElement: HTMLFormElement) => {
  return emailjs.sendForm(
    import.meta.env.VITE_EMAILJS_SERVICE_ID as string,
    import.meta.env.VITE_EMAILJS_TEMPLATE_ID as string,
    formElement,
    import.meta.env.VITE_EMAILJS_PUBLIC_KEY as string
  )
}
