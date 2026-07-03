import { useNavigate } from 'react-router-dom'
import { ChevronLeft } from 'lucide-react'
import { cn } from '@/lib/utils'

interface AppHeaderProps {
  title: string
  showBack?: boolean
  action?: React.ReactNode
  className?: string
}

export default function AppHeader({
  title,
  showBack = true,
  action,
  className,
}: AppHeaderProps) {
  const navigate = useNavigate()

  return (
    <header
      className={cn(
        'bg-[#1B4332] flex items-center gap-3 px-4 py-4',
        className,
      )}
    >
      {showBack ? (
        <button
          onClick={() => navigate(-1)}
          aria-label="Go back"
          className="w-9 h-9 rounded-[10px] bg-white/10 flex items-center justify-center flex-none"
        >
          <ChevronLeft size={20} color="#F8F5F0" strokeWidth={2.5} aria-hidden="true" />
        </button>
      ) : (
        <div className="w-9 flex-none" />
      )}

      <h1 className="flex-1 text-center text-base font-bold text-[#F8F5F0] m-0">
        {title}
      </h1>

      {action ? (
        <div className="w-9 flex-none flex justify-end">{action}</div>
      ) : (
        <div className="w-9 flex-none" />
      )}
    </header>
  )
}
