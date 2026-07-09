import { useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { authApi } from '@/api/auth'
import { usePageTitle } from '@/hooks/usePageTitle'

export default function ResetPasswordPage() {
  usePageTitle('Reset password')
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') ?? ''
  const navigate = useNavigate()
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)

  const { mutate, isPending } = useMutation({
    mutationFn: () => authApi.resetPassword(token, password),
    onSuccess: () => setDone(true),
    onError: (err: unknown) => {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(detail ?? 'Something went wrong. Please try again.')
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (!token) { setError('Invalid or missing reset token.'); return }
    if (password.length < 8) { setError('Password must be at least 8 characters.'); return }
    if (password !== confirm) { setError('Passwords do not match.'); return }
    mutate()
  }

  if (!token) {
    return (
      <div className="flex flex-col flex-1 px-7 pt-16 pb-10 items-center text-center gap-4">
        <p className="text-base font-semibold text-[#B4472F]">Invalid reset link.</p>
        <Link to="/forgot-password" className="text-[#1B4332] font-semibold text-sm no-underline">
          Request a new one
        </Link>
      </div>
    )
  }

  return (
    <div className="flex flex-col flex-1 px-7 pt-16 pb-10">
      <div className="flex flex-col gap-2 mb-8">
        <h1 className="text-2xl font-extrabold text-[#1B4332] tracking-[-0.5px] m-0">
          Set new password
        </h1>
        <p className="text-sm text-[#6B7268] m-0">
          Choose a strong password for your Vilapay account.
        </p>
      </div>

      {done ? (
        <div className="flex flex-col items-center gap-4 mt-4 text-center">
          <div className="w-14 h-14 rounded-full bg-[#E8F5EE] flex items-center justify-center">
            <span className="text-[#1B4332] text-2xl">✓</span>
          </div>
          <p className="text-base font-semibold text-[#1F2A24]">Password updated!</p>
          <p className="text-sm text-[#6B7268]">You can now sign in with your new password.</p>
          <button
            onClick={() => navigate('/login', { replace: true })}
            className="mt-4 w-full py-4 bg-[#1B4332] text-[#F8F5F0] rounded-xl text-base font-bold border-none cursor-pointer hover:bg-[#173A2B] transition-colors"
          >
            Sign in
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-[14px]">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="password" className="text-[13px] font-semibold text-[#3E4A42]">
              New password
            </label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              placeholder="At least 8 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-[14px] border border-[#DDD6C8] rounded-xl bg-white text-base text-[#1F2A24] focus:outline-[2px] focus:outline-[#1B4332] focus:outline-offset-0"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="confirm" className="text-[13px] font-semibold text-[#3E4A42]">
              Confirm password
            </label>
            <input
              id="confirm"
              type="password"
              autoComplete="new-password"
              placeholder="Repeat your password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
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
            {isPending ? 'Saving…' : 'Set new password'}
          </button>
        </form>
      )}
    </div>
  )
}
