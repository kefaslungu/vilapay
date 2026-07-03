import { useNavigate } from 'react-router-dom'
import { Edit2, Lock, HelpCircle, MessageCircle, LogOut, ChevronRight } from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { initials } from '@/lib/utils'

interface Row {
  icon: React.ReactNode
  label: string
  onPress: () => void
  danger?: boolean
}

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  function doLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  const accountRows: Row[] = [
    {
      icon: <Edit2 size={20} color="#1B4332" aria-hidden="true" />,
      label: 'Edit profile',
      onPress: () => {},
    },
    {
      icon: <Lock size={20} color="#1B4332" aria-hidden="true" />,
      label: 'Change PIN',
      onPress: () => {},
    },
  ]

  const supportRows: Row[] = [
    {
      icon: <HelpCircle size={20} color="#1B4332" aria-hidden="true" />,
      label: 'Help & FAQ',
      onPress: () => {},
    },
    {
      icon: <MessageCircle size={20} color="#1B4332" aria-hidden="true" />,
      label: 'Contact us',
      onPress: () => {},
    },
  ]

  return (
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
        {/* Account section */}
        <Section label="Account" rows={accountRows} />

        {/* Support section */}
        <Section label="Support" rows={supportRows} />

        {/* Danger zone */}
        <div className="flex flex-col gap-2">
          <span className="text-[12px] font-bold text-[#B4472F] uppercase tracking-[0.6px] pl-1">
            Danger zone
          </span>
          <div className="bg-white border border-[#E8E2D6] rounded-2xl overflow-hidden">
            <button
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
  )
}

function Section({ label, rows }: { label: string; rows: Row[] }) {
  return (
    <div className="flex flex-col gap-2">
      <span className="text-[12px] font-bold text-[#6B7268] uppercase tracking-[0.6px] pl-1">
        {label}
      </span>
      <div className="bg-white border border-[#E8E2D6] rounded-2xl overflow-hidden">
        {rows.map((row, i) => (
          <button
            key={row.label}
            onClick={row.onPress}
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
