import { Outlet, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/auth'

export default function AuthLayout() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated())
  if (isAuthenticated) return <Navigate to="/dashboard" replace />

  return (
    <div className="w-full max-w-[480px] bg-[#F8F5F0] min-h-svh shadow-[0_0_48px_rgba(27,67,50,0.10)] flex flex-col">
      <Outlet />
    </div>
  )
}
