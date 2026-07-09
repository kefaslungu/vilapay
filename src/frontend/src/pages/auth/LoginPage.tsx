import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { Eye, EyeOff } from 'lucide-react'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/store/auth'
import { usePageTitle } from '@/hooks/usePageTitle'

export default function LoginPage() {
  usePageTitle('Sign in')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)

  const { mutate, isPending } = useMutation({
    mutationFn: () => authApi.login(email, password),
    onSuccess: (data) => {
      setAuth(data.access, data.user)
      navigate('/dashboard', { replace: true })
    },
    onError: () => setError('Invalid email or password.'),
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (!email.trim()) { setError('Email is required.'); return }
    if (!password.trim()) { setError('Password is required.'); return }
    mutate()
  }

  return (
    <div className="flex flex-col flex-1 px-7 pt-16 pb-10">
      {/* Logo */}
      <div className="flex flex-col items-center gap-[14px] mb-11">
        <div className="relative w-16 h-16 bg-[#1B4332] rounded-[18px] flex items-center justify-center">
          <span className="text-[#F8F5F0] text-[30px] font-extrabold tracking-[-1px]">V</span>
          <span className="absolute right-[10px] bottom-[10px] w-[9px] h-[9px] bg-[#D4A853] rounded-full" />
        </div>
        <div className="flex flex-col items-center gap-1">
          <span className="text-[26px] font-extrabold text-[#1B4332] tracking-[-0.5px]">
            Vilapay
          </span>
          <span className="text-sm text-[#6B7268]">Save together. Get paid in turn.</span>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-[14px]">
        <div className="flex flex-col gap-1.5">
          <label htmlFor="email" className="text-[13px] font-semibold text-[#3E4A42]">
            Email
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

        <div className="flex flex-col gap-1.5">
          <label htmlFor="password" className="text-[13px] font-semibold text-[#3E4A42]">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-[14px] pr-12 border border-[#DDD6C8] rounded-xl bg-white text-base text-[#1F2A24] focus:outline-[2px] focus:outline-[#1B4332] focus:outline-offset-0"
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-[#6B7268] bg-transparent border-none cursor-pointer p-1"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
        </div>

        <Link
          to="/forgot-password"
          className="self-end text-[13px] font-semibold text-[#1B4332] no-underline"
        >
          Forgot password?
        </Link>

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
          {isPending ? 'Signing in…' : 'Sign in'}
        </button>
      </form>

      <div className="mt-auto pt-8 flex justify-center gap-1.5 text-sm">
        <span className="text-[#6B7268]">New to Vilapay?</span>
        <Link to="/register" className="font-bold text-[#1B4332] no-underline">
          Register
        </Link>
      </div>
    </div>
  )
}
