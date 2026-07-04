import { useNavigate } from 'react-router-dom'
import { usePageTitle } from '@/hooks/usePageTitle'

export default function NotFoundPage() {
  usePageTitle('Page not found')
  const navigate = useNavigate()

  return (
    <main className="flex-1 flex flex-col items-center justify-center text-center px-8 gap-2">
      <span className="text-[96px] font-extrabold text-[#1B4332] leading-none tracking-[-3px]">
        404
      </span>
      <span className="w-11 h-1 bg-[#D4A853] rounded-sm my-3 block" />
      <h1 className="text-[22px] font-extrabold text-[#1F2A24] m-0">
        Page not found
      </h1>
      <p className="text-[15px] text-[#6B7268] leading-relaxed max-w-[300px]">
        This link may be broken or the page has been removed.
      </p>
      <button
        onClick={() => navigate('/dashboard', { replace: true })}
        className="mt-6 px-8 py-4 bg-[#1B4332] text-[#F8F5F0] rounded-xl text-base font-bold hover:bg-[#173A2B] transition-colors cursor-pointer border-none"
      >
        Go back home
      </button>
    </main>
  )
}
