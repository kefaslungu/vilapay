import { NavLink } from 'react-router-dom'
import { Home, TrendingUp, PlusCircle, User } from 'lucide-react'
import { cn } from '@/lib/utils'

const tabs = [
  { to: '/dashboard', label: 'Home', Icon: Home },
  { to: '/history', label: 'History', Icon: TrendingUp },
  { to: '/groups/new', label: 'New group', Icon: PlusCircle },
  { to: '/profile', label: 'Profile', Icon: User },
]

export default function BottomNav() {
  return (
    <nav
      aria-label="Main navigation"
      className="sticky bottom-0 mt-auto bg-white border-t border-[#E8E2D6] flex"
      style={{ paddingBottom: 'calc(8px + env(safe-area-inset-bottom))' }}
    >
      {tabs.map(({ to, label, Icon }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) =>
            cn(
              'flex-1 flex flex-col items-center gap-1 py-2 text-[11px] font-semibold no-underline transition-colors',
              isActive ? 'text-[#1B4332]' : 'text-[#A8A296]',
            )
          }
        >
          {({ isActive }) => (
            <>
              <Icon
                size={22}
                strokeWidth={isActive ? 2.5 : 2}
                aria-hidden="true"
              />
              <span>{label}</span>
            </>
          )}
        </NavLink>
      ))}
    </nav>
  )
}
