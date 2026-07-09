import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Edit2, Lock, HelpCircle, MessageCircle, LogOut, ChevronRight, X, Eye, EyeOff } from 'lucide-react'
import { useMutation } from '@tanstack/react-query'
import { useAuthStore } from '@/store/auth'
import { authApi } from '@/api/auth'
import { initials } from '@/lib/utils'
import { usePageTitle } from '@/hooks/usePageTitle'

// ---------------------------------------------------------------------------
// BottomSheet
// ---------------------------------------------------------------------------
function BottomSheet({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
}) {
  if (!open) return null
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label={title}
      className="fixed inset-0 z-50 flex flex-col justify-end"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
        aria-hidden="true"
      />
      {/* Sheet */}
      <div className="relative bg-white rounded-t-[24px] px-5 pt-5 pb-10 flex flex-col gap-5 max-h-[90dvh] overflow-y-auto">
        {/* Handle + header */}
        <div className="flex items-center justify-between">
          <span className="text-[17px] font-extrabold text-[#1F2A24]">{title}</span>
          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-full bg-[#F1EDE4] border-none cursor-pointer"
            aria-label="Close"
          >
            <X size={16} color="#6B7268" />
          </button>
        </div>
        {children}
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// EditProfileSheet — read-only
// ---------------------------------------------------------------------------
function EditProfileSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const user = useAuthStore((s) => s.user)
  return (
    <BottomSheet open={open} onClose={onClose} title="Your profile">
      <div className="flex flex-col gap-4">
        <p className="text-[13px] text-[#6B7268] m-0">
          Your name and phone number are verified against your identity documents. To request
          changes, contact{' '}
          <a
            href="mailto:support@vilapay.com"
            className="text-[#1B4332] font-semibold no-underline"
          >
            support@vilapay.com
          </a>
          .
        </p>

        {[
          { label: 'Full name', value: user?.full_name },
          { label: 'Email', value: user?.email },
          { label: 'Phone number', value: user?.phone_number },
        ].map(({ label, value }) => (
          <div key={label} className="flex flex-col gap-1">
            <span className="text-[12px] font-semibold text-[#6B7268] uppercase tracking-[0.5px]">
              {label}
            </span>
            <div className="px-4 py-[13px] bg-[#F8F5F0] border border-[#E8E2D6] rounded-xl text-[15px] font-semibold text-[#1F2A24]">
              {value ?? '—'}
            </div>
          </div>
        ))}
      </div>
    </BottomSheet>
  )
}

// ---------------------------------------------------------------------------
// ChangePasswordSheet
// ---------------------------------------------------------------------------
function ChangePasswordSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showCurrent, setShowCurrent] = useState(false)
  const [showNext, setShowNext] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(false)

  const { mutate, isPending } = useMutation({
    mutationFn: () => authApi.changePassword(current, next),
    onSuccess: () => {
      setDone(true)
      setCurrent('')
      setNext('')
      setConfirm('')
    },
    onError: (err: unknown) => {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setError(detail ?? 'Something went wrong. Please try again.')
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    if (!current) { setError('Enter your current password.'); return }
    if (next.length < 8) { setError('New password must be at least 8 characters.'); return }
    if (next !== confirm) { setError('Passwords do not match.'); return }
    mutate()
  }

  function handleClose() {
    setDone(false)
    setError('')
    setCurrent('')
    setNext('')
    setConfirm('')
    onClose()
  }

  return (
    <BottomSheet open={open} onClose={handleClose} title="Change password">
      {done ? (
        <div className="flex flex-col items-center gap-4 py-4 text-center">
          <div className="w-14 h-14 rounded-full bg-[#E8F5EE] flex items-center justify-center">
            <span className="text-[#1B4332] text-2xl" aria-hidden="true">✓</span>
          </div>
          <p className="text-base font-semibold text-[#1F2A24] m-0">Password updated!</p>
          <p className="text-sm text-[#6B7268] m-0">Use your new password next time you sign in.</p>
          <button
            type="button"
            onClick={handleClose}
            className="w-full py-4 mt-2 bg-[#1B4332] text-[#F8F5F0] rounded-xl text-base font-bold border-none cursor-pointer hover:bg-[#173A2B] transition-colors"
          >
            Done
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-[14px]">
          <PasswordField
            id="current-password"
            label="Current password"
            value={current}
            onChange={setCurrent}
            show={showCurrent}
            onToggle={() => setShowCurrent((v) => !v)}
            autoComplete="current-password"
            placeholder="Your current password"
          />
          <PasswordField
            id="new-password"
            label="New password"
            value={next}
            onChange={setNext}
            show={showNext}
            onToggle={() => setShowNext((v) => !v)}
            autoComplete="new-password"
            placeholder="At least 8 characters"
          />
          <PasswordField
            id="confirm-password"
            label="Confirm new password"
            value={confirm}
            onChange={setConfirm}
            show={showConfirm}
            onToggle={() => setShowConfirm((v) => !v)}
            autoComplete="new-password"
            placeholder="Repeat new password"
          />

          {error && (
            <p role="alert" className="text-sm text-[#B4472F] m-0">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isPending}
            className="w-full py-4 mt-1 bg-[#1B4332] text-[#F8F5F0] rounded-xl text-base font-bold border-none cursor-pointer hover:bg-[#173A2B] transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {isPending ? 'Saving…' : 'Update password'}
          </button>
        </form>
      )}
    </BottomSheet>
  )
}

function PasswordField({
  id,
  label,
  value,
  onChange,
  show,
  onToggle,
  autoComplete,
  placeholder,
}: {
  id: string
  label: string
  value: string
  onChange: (v: string) => void
  show: boolean
  onToggle: () => void
  autoComplete: string
  placeholder: string
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-[13px] font-semibold text-[#3E4A42]">
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          type={show ? 'text' : 'password'}
          autoComplete={autoComplete}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          required
          className="w-full px-4 py-[14px] pr-12 border border-[#DDD6C8] rounded-xl bg-white text-base text-[#1F2A24] focus:outline-[2px] focus:outline-[#1B4332] focus:outline-offset-0"
        />
        <button
          type="button"
          onClick={onToggle}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-[#6B7268] bg-transparent border-none cursor-pointer p-1"
          aria-label={show ? 'Hide password' : 'Show password'}
        >
          {show ? <EyeOff size={18} /> : <Eye size={18} />}
        </button>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// HelpFaqSheet — static
// ---------------------------------------------------------------------------
function HelpFaqSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  const faqs = [
    {
      q: 'What is a savings group?',
      a: 'A savings group (ajo/esusu) is a rotating pot where members contribute regularly and each member receives the full pot in turn.',
    },
    {
      q: 'How do I join a group?',
      a: 'Ask the group creator to share the invite code. Tap the "+" on the Groups screen and enter the code, or accept an invite link.',
    },
    {
      q: 'When will I receive my payout?',
      a: 'Payouts follow the order set by the group admin. You can see your position and payout date on the group detail screen.',
    },
    {
      q: 'What tiers are available?',
      a: 'Free (1 group), Individual Pro (5 groups), and Collector Pro (unlimited). Upgrade on the Plans screen.',
    },
    {
      q: 'Is my money safe?',
      a: 'Contributions are processed through Nomba, a licensed payment institution. Funds are held securely until payout.',
    },
  ]

  return (
    <BottomSheet open={open} onClose={onClose} title="Help & FAQ">
      <div className="flex flex-col gap-4">
        {faqs.map(({ q, a }) => (
          <div key={q} className="flex flex-col gap-1">
            <span className="text-[14px] font-bold text-[#1F2A24]">{q}</span>
            <span className="text-[13px] text-[#6B7268] leading-relaxed">{a}</span>
          </div>
        ))}
      </div>
    </BottomSheet>
  )
}

// ---------------------------------------------------------------------------
// ContactUsSheet — static
// ---------------------------------------------------------------------------
function ContactUsSheet({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <BottomSheet open={open} onClose={onClose} title="Contact us">
      <div className="flex flex-col gap-3">
        <p className="text-[13px] text-[#6B7268] m-0">
          We're here to help. Reach us through any of the channels below.
        </p>
        {[
          { label: 'Email support', value: 'support@vilapay.com', href: 'mailto:support@vilapay.com' },
          { label: 'WhatsApp', value: '+234 800 000 0000', href: 'https://wa.me/2348000000000' },
        ].map(({ label, value, href }) => (
          <a
            key={label}
            href={href}
            target="_blank"
            rel="noreferrer"
            className="flex flex-col gap-0.5 px-4 py-[13px] bg-[#F8F5F0] border border-[#E8E2D6] rounded-xl no-underline"
          >
            <span className="text-[12px] font-semibold text-[#6B7268] uppercase tracking-[0.5px]">
              {label}
            </span>
            <span className="text-[15px] font-semibold text-[#1B4332]">{value}</span>
          </a>
        ))}
      </div>
    </BottomSheet>
  )
}

// ---------------------------------------------------------------------------
// ProfilePage
// ---------------------------------------------------------------------------
type Sheet = 'edit' | 'password' | 'faq' | 'contact' | null

interface Row {
  icon: React.ReactNode
  label: string
  sheet: Sheet
  danger?: boolean
}

export default function ProfilePage() {
  usePageTitle('Profile')
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()
  const [activeSheet, setActiveSheet] = useState<Sheet>(null)

  function doLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  const accountRows: Row[] = [
    {
      icon: <Edit2 size={20} color="#1B4332" aria-hidden="true" />,
      label: 'Edit profile',
      sheet: 'edit',
    },
    {
      icon: <Lock size={20} color="#1B4332" aria-hidden="true" />,
      label: 'Change password',
      sheet: 'password',
    },
  ]

  const supportRows: Row[] = [
    {
      icon: <HelpCircle size={20} color="#1B4332" aria-hidden="true" />,
      label: 'Help & FAQ',
      sheet: 'faq',
    },
    {
      icon: <MessageCircle size={20} color="#1B4332" aria-hidden="true" />,
      label: 'Contact us',
      sheet: 'contact',
    },
  ]

  return (
    <>
      <div className="flex flex-col flex-1">
        {/* Green header */}
        <header className="bg-[#1B4332] px-6 pt-7 pb-8 rounded-b-[28px] flex flex-col items-center gap-3">
          <h1 className="self-start text-[22px] font-extrabold text-[#F8F5F0] tracking-[-0.3px] m-0">
            Profile
          </h1>
          <div
            className="w-[76px] h-[76px] rounded-full bg-[#D4A853] flex items-center justify-center font-extrabold text-[26px] text-[#1B4332] mt-1.5"
            aria-label={`${user?.full_name} avatar`}
          >
            {initials(user?.full_name ?? '')}
          </div>
          <div className="flex flex-col items-center gap-0.5">
            <span className="text-lg font-bold text-[#F8F5F0]">{user?.full_name}</span>
            <span className="text-[13px] text-[#A9C0B2]">{user?.email}</span>
          </div>
        </header>

        <div className="flex flex-col gap-[22px] px-5 py-6">
          <Section label="Account" rows={accountRows} onOpen={(s) => setActiveSheet(s)} />
          <Section label="Support" rows={supportRows} onOpen={(s) => setActiveSheet(s)} />

          {/* Danger zone */}
          <div className="flex flex-col gap-2">
            <span className="text-[12px] font-bold text-[#B4472F] uppercase tracking-[0.6px] pl-1">
              Danger zone
            </span>
            <div className="bg-white border border-[#E8E2D6] rounded-2xl overflow-hidden">
              <button
                type="button"
                onClick={doLogout}
                className="w-full flex items-center gap-3 px-4 py-[15px] bg-transparent border-none cursor-pointer hover:bg-[#FBF1EE] transition-colors"
              >
                <LogOut size={20} color="#B4472F" aria-hidden="true" />
                <span className="flex-1 text-left text-[15px] font-bold text-[#B4472F]">
                  Log out
                </span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom sheets */}
      <EditProfileSheet open={activeSheet === 'edit'} onClose={() => setActiveSheet(null)} />
      <ChangePasswordSheet open={activeSheet === 'password'} onClose={() => setActiveSheet(null)} />
      <HelpFaqSheet open={activeSheet === 'faq'} onClose={() => setActiveSheet(null)} />
      <ContactUsSheet open={activeSheet === 'contact'} onClose={() => setActiveSheet(null)} />
    </>
  )
}

function Section({
  label,
  rows,
  onOpen,
}: {
  label: string
  rows: Row[]
  onOpen: (s: Sheet) => void
}) {
  return (
    <div className="flex flex-col gap-2">
      <span className="text-[12px] font-bold text-[#6B7268] uppercase tracking-[0.6px] pl-1">
        {label}
      </span>
      <div className="bg-white border border-[#E8E2D6] rounded-2xl overflow-hidden">
        {rows.map((row, i) => (
          <button
            key={row.label}
            type="button"
            onClick={() => onOpen(row.sheet)}
            className="w-full flex items-center gap-3 px-4 py-[15px] bg-transparent border-none cursor-pointer hover:bg-[#FAF8F3] transition-colors"
            style={{ borderBottom: i < rows.length - 1 ? '1px solid #F1EDE4' : 'none' }}
          >
            {row.icon}
            <span className="flex-1 text-left text-[15px] font-semibold text-[#1F2A24]">
              {row.label}
            </span>
            <ChevronRight size={18} color="#A8A296" aria-hidden="true" />
          </button>
        ))}
      </div>
    </div>
  )
}
