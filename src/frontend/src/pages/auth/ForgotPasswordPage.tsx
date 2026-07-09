import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { ChevronLeft } from 'lucide-react'
import { authApi } from '@/api/auth'
import { usePageTitle } from '@/hooks/usePageTitle'

export default function ForgotPasswordPage() {
  usePageTitle('Forgot password')
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [error, setError] = useState('')

  const { mutate, isPending } = useMutation({
    mutationFn: () => authApi.forgotPassword(email),
    onSuccess: () => setSent(true),
    onError: () => setError('Something went wrong. Please try again.'),
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (!email.trim()) { setError('Email is required.'); return }
    mutate()
  }

  return (
    <div className="flex flex-col flex-1 px-7 pt-10 pb-10">
      <Link
        to="/login"
        className="flex items-center gap-1 text-[#1B4332] font-semibold text-sm no-underline mb-8 self-start"
      >
        <ChevronLeft size={18} strokeWidth={2.5} />
        Back to sign in
      </Link>

      <div className="flex flex-col gap-2 mb-8">
        <h1 className="text-2xl font-extrabold text-[#1B4332] tracking-[-0.5px] m-0">
          Forgot password?
        </h1>
        <p className="text-sm text-[#6B7268] m-0">
          Enter your email and we'll send you a link to reset your password.
        </p>
      </div>

      {sent ? (
        <div className="flex flex-col items-center gap-4 mt-8 text-center">
          <div className="w-14 h-14 rounded-full bg-[#E8F5EE] flex items-center justify-center">
            <span className="text-[#1B4332] text-2xl">✓</span>
          </div>
          <p className="text-base font-semibold text-[#1F2A24]">Check your email</p>
          <p className="text-sm text-[#6B7268]">
            If <span className="font-semibold text-[#1F2A24]">{email}</span> is registered, a
            reset link is on its way. Check your spam folder if you don't see it.
          </p>
          <Link
            to="/login"
            className="mt-4 w-full py-4 bg-[#1B4332] text-[#F8F5F0] rounded-xl text-base font-bold text-center no-underline block"
          >
            Back to sign in
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-[14px]">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="email" className="text-[13px] font-semibold text-[#3E4A42]">
              Email address
            </label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-[14px] border border-[#DDD6C8] rounded-xl bg-white text-base text-[#1F2A24] focus:outline-[2px] focus:outline-[#1B4332] focus:outline-offset-0"
            />
          </div>

          {error && (
            <p role="alert" className="text-sm text-[#B4472F] m-0">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isPending}
            className="w-full py-4 mt-1.5 bg-[#1B4332] text-[#F8F5F0] rounded-xl text-base font-bold border-none cursor-pointer hover:bg-[#173A2B] transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isPending ? 'Sending…' : 'Send reset link'}
          </button>
        </form>
      )}
    </div>
  )
}
