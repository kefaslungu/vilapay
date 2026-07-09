import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ChevronRight, Users } from 'lucide-react'
import { useAuthStore } from '@/store/auth'
import { walletApi } from '@/api/wallet'
import { groupsApi } from '@/api/groups'
import { naira, initials } from '@/lib/utils'
import { usePageTitle } from '@/hooks/usePageTitle'

function greeting() {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
}

export default function DashboardPage() {
  usePageTitle('Home')
  const user = useAuthStore((s) => s.user)
  const navigate = useNavigate()

  const { data: wallet } = useQuery({
    queryKey: ['wallet'],
    queryFn: walletApi.mine,
  })

  const { data: memberships = [] } = useQuery({
    queryKey: ['memberships'],
    queryFn: groupsApi.myMemberships,
  })

  const firstName = user?.full_name.split(' ')[0] ?? ''
  const userInitials = initials(user?.full_name ?? '')

  const nextPayout = memberships
    .map((m) => m.next_payout_date)
    .filter((d): d is string => !!d)
    .sort()[0]

  const nextPayoutLabel = nextPayout
    ? new Date(nextPayout).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
    : '—'

  return (
    <div className="flex flex-col flex-1">
      {/* Green header */}
      <header className="bg-[#1B4332] px-6 pt-6 pb-[68px] rounded-b-[28px]">
        <div className="flex items-center justify-between mb-6">
          <div className="flex flex-col gap-0.5">
            <span className="text-[13px] text-[#A9C0B2]">{greeting()},</span>
            <span className="text-[22px] font-extrabold text-[#F8F5F0] tracking-[-0.3px]">
              {firstName}
            </span>
          </div>
          <div
            className="w-11 h-11 rounded-full bg-[#D4A853] flex items-center justify-center font-bold text-base text-[#1B4332]"
            aria-label={`${user?.full_name} avatar`}
          >
            {userInitials}
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <span className="text-[13px] text-[#A9C0B2]">Wallet balance</span>
          <span className="text-[34px] font-extrabold text-[#F8F5F0] tracking-[-0.5px]">
            {wallet ? naira(parseFloat(wallet.balance)) : '—'}
          </span>
        </div>
      </header>

      {/* Stat cards */}
      <div className="flex gap-3 px-5 -mt-10">
        <div className="flex-1 bg-white border border-[#E8E2D6] rounded-2xl p-4 flex flex-col gap-1 shadow-[0_4px_14px_rgba(27,67,50,0.07)]">
          <span className="text-[12px] font-semibold text-[#6B7268]">Active groups</span>
          <span className="text-2xl font-extrabold text-[#1B4332]">
            {memberships.length}
          </span>
        </div>
        <div className="flex-1 bg-white border border-[#E8E2D6] rounded-2xl p-4 flex flex-col gap-1 shadow-[0_4px_14px_rgba(27,67,50,0.07)]">
          <span className="text-[12px] font-semibold text-[#6B7268]">Next payout</span>
          <div className="flex items-baseline gap-1.5">
            <span className="text-2xl font-extrabold text-[#1B4332]">{nextPayoutLabel}</span>
            {nextPayout && <span className="w-2 h-2 bg-[#D4A853] rounded-full" />}
          </div>
        </div>
      </div>

      {/* Group list */}
      <section className="flex flex-col gap-3 px-5 pt-7 pb-6">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-[#1F2A24] m-0">Your groups</h2>
          <button
            onClick={() => navigate('/groups/new')}
            className="text-[13px] font-bold text-[#1B4332] bg-transparent border-none cursor-pointer"
          >
            + New group
          </button>
        </div>

        {memberships.length === 0 ? (
          /* Empty state */
          <div className="bg-white border border-[#E8E2D6] rounded-2xl px-6 py-8 flex flex-col items-center text-center gap-4">
            <div className="w-16 h-16 rounded-[20px] bg-[#DCE9E1] flex items-center justify-center">
              <Users size={30} color="#1B4332" aria-hidden="true" />
            </div>
            <div className="flex flex-col gap-1.5">
              <span className="text-base font-bold text-[#1F2A24]">No groups yet</span>
              <p className="text-sm text-[#6B7268] leading-relaxed m-0 max-w-[260px]">
                You haven't joined any ajo group yet. Start one or join with an invite code.
              </p>
            </div>
            <button
              onClick={() => navigate('/groups/new')}
              className="flex items-center gap-2 px-[22px] py-[13px] bg-[#1B4332] text-[#F8F5F0] rounded-xl text-[15px] font-bold border-none cursor-pointer hover:bg-[#173A2B] transition-colors"
            >
              Start or join a group
            </button>
          </div>
        ) : (
          memberships.map(({ group, next_payout_date }) => {
            const statusLabel: Record<string, string> = {
              pending: 'Pending',
              active: 'Active',
              completed: 'Completed',
              cancelled: 'Cancelled',
            }
            const statusColors: Record<string, { text: string; bg: string }> = {
              pending:   { text: '#6B7268', bg: '#EFEBE2' },
              active:    { text: '#8A6A1F', bg: '#F3E5C3' },
              completed: { text: '#1B4332', bg: '#DCE9E1' },
              cancelled: { text: '#B4472F', bg: '#FAEAE6' },
            }
            const sc = statusColors[group.status] ?? statusColors.active
            const payoutLabel = next_payout_date
              ? new Date(next_payout_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
              : null

            return (
              <button
                key={group.id}
                onClick={() => navigate(`/groups/${group.id}`)}
                className="w-full text-left bg-white border border-[#E8E2D6] rounded-2xl p-4 flex flex-col gap-3 cursor-pointer hover:border-[#1B4332] hover:shadow-[0_4px_14px_rgba(27,67,50,0.08)] transition-all"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex flex-col gap-0.5 min-w-0">
                    <span className="text-[15px] font-bold text-[#1F2A24] truncate">
                      {group.name}
                    </span>
                    <span className="text-[13px] text-[#6B7268]">
                      {naira(parseFloat(group.contribution_amount))} ·{' '}
                      {group.frequency.charAt(0).toUpperCase() + group.frequency.slice(1)} ·{' '}
                      {group.slot_count} members
                    </span>
                  </div>
                  <ChevronRight size={18} color="#A8A296" className="flex-none" aria-hidden="true" />
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-[12px] text-[#6B7268]">
                    {payoutLabel ? `Next payout: ${payoutLabel}` : 'No upcoming payout'}
                  </span>
                  <span
                    className="text-[12px] font-semibold px-2 py-0.5 rounded-full"
                    style={{ color: sc.text, background: sc.bg }}
                  >
                    {statusLabel[group.status] ?? group.status}
                  </span>
                </div>
              </button>
            )
          })
        )}
      </section>
    </div>
  )
}
