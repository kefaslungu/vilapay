import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { ChevronLeft } from 'lucide-react'
import { authApi } from '@/api/auth'
import { useAuthStore } from '@/store/auth'
import { parseDrfError } from '@/lib/utils'

export default function RegisterPage() {
  const [form, setForm] = useState({
    full_name: '',
    email: '',
    phone_number: '',
    password: '',
  })
  const [error, setError] = useState('')
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)

  const { mutate, isPending } = useMutation({
    mutationFn: () =>
      authApi.register({
        full_name: form.full_name,
        email: form.email,
        phone_number: `+234${form.phone_number}`,
        password: form.password,
      }),
    onSuccess: (data) => {
      setAuth(data.access, data.user)
      navigate('/dashboard', { replace: true })
    },
    onError: (err: unknown) => {
      setError(parseDrfError(err, 'Registration failed. Please try again.'))
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (!form.full_name.trim()) { setError('Full name is required.'); return }
    if (!form.email.trim()) { setError('Email is required.'); return }
    if (!form.phone_number.trim()) { setError('Phone number is required.'); return }
    if (form.password.length < 8) { setError('Password must be at least 8 characters.'); return }
    mutate()
  }

  function set(key: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value }))
  }

  return (
    <div className="flex flex-col flex-1 px-7 pt-7 pb-10">
      {/* Back */}
      <Link
        to="/login"
        className="flex items-center gap-1.5 text-[#1B4332] text-sm font-semibold no-underline mb-7"
      >
        <ChevronLeft size={18} strokeWidth={2.5} aria-hidden="true" />
        Back
      </Link>

      {/* Heading */}
      <div className="flex flex-col gap-1.5 mb-7">
        <h1 className="text-[26px] font-extrabold text-[#1B4332] tracking-[-0.5px] m-0">
          Create your account
        </h1>
        <p className="text-sm text-[#6B7268] leading-relaxed m-0">
          Join thousands saving the ajo way — with receipts.
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-[14px]">
        <div className="flex flex-col gap-1.5">
          <label htmlFor="full_name" className="text-[13px] font-semibold text-[#3E4A42]">
            Full name
          </label>
          <input
            id="full_name"
            type="text"
            autoComplete="name"
            placeholder="e.g. Adaeze Okafor"
            value={form.full_name}
            onChange={set('full_name')}
            required
            className="w-full px-4 py-[14px] border border-[#DDD6C8] rounded-xl bg-white text-base text-[#1F2A24] focus:outline-[2px] focus:outline-[#1B4332] focus:outline-offset-0"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="email" className="text-[13px] font-semibold text-[#3E4A42]">
            Email
          </label>
          <input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="you@example.com"
            value={form.email}
            onChange={set('email')}
            required
            className="w-full px-4 py-[14px] border border-[#DDD6C8] rounded-xl bg-white text-base text-[#1F2A24] focus:outline-[2px] focus:outline-[#1B4332] focus:outline-offset-0"
          />
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="phone_number" className="text-[13px] font-semibold text-[#3E4A42]">
            Phone number
          </label>
          <div className="flex gap-2">
            <span className="flex items-center px-[14px] bg-[#EFEBE2] border border-[#DDD6C8] rounded-xl text-[15px] font-semibold text-[#3E4A42] whitespace-nowrap">
              +234
            </span>
            <input
              id="phone_number"
              type="tel"
              autoComplete="tel-national"
              placeholder="801 234 5678"
              value={form.phone_number}
              onChange={set('phone_number')}
              required
              className="flex-1 min-w-0 px-4 py-[14px] border border-[#DDD6C8] rounded-xl bg-white text-base text-[#1F2A24] focus:outline-[2px] focus:outline-[#1B4332] focus:outline-offset-0"
            />
          </div>
        </div>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="password" className="text-[13px] font-semibold text-[#3E4A42]">
            Password
          </label>
          <input
            id="password"
            type="password"
            autoComplete="new-password"
            placeholder="At least 8 characters"
            value={form.password}
            onChange={set('password')}
            required
            minLength={8}
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
          {isPending ? 'Creating account…' : 'Create account'}
        </button>
      </form>

      <div className="mt-auto pt-8 flex justify-center gap-1.5 text-sm">
        <span className="text-[#6B7268]">Already have an account?</span>
        <Link to="/login" className="font-bold text-[#1B4332] no-underline">
          Sign in
        </Link>
      </div>
    </div>
  )
}
