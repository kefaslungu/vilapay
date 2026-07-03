import { Outlet } from 'react-router-dom'
import BottomNav from './BottomNav'

export default function AppLayout() {
  return (
    <div className="w-full max-w-[480px] bg-[#F8F5F0] min-h-svh shadow-[0_0_48px_rgba(27,67,50,0.10)] flex flex-col">
      <Outlet />
      <BottomNav />
    </div>
  )
}
