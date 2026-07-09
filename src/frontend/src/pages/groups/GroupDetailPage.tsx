import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ChevronLeft } from 'lucide-react'
import client from '@/api/client'
import { naira, initials } from '@/lib/utils'
import { usePageTitle } from '@/hooks/usePageTitle'
import { useAuthStore } from '@/store/auth'
import type { GroupCycle } from '@/types'

interface MemberDetail {
  id: string
  slot_number: number
  status: string
  user_name: string
  user_email: string
}

interface GroupDetail {
  id: string
  name: string
  slot_count: number
  contribution_amount: string
  frequency: string
  status: string
  invite_code: string
  virtual_account?: { account_number: string; bank_name: string }
}

const avatarPalette = [
  { bg: '#DCE9E1', color: '#1B4332' },
  { bg: '#F3E5C3', color: '#8A6A1F' },
  { bg: '#E8E2D6', color: '#3E4A42' },
]

export default function GroupDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const [copied, setCopied] = useState(false)
  const [copyFailed, setCopyFailed] = useState(false)
  const [payLoading, setPayLoading] = useState(false)
  const [payError, setPayError] = useState<string | null>(null)

  const { data: group } = useQuery<GroupDetail>({
    queryKey: ['group', id],
    queryFn: () => client.get<GroupDetail>(`/groups/${id}/`).then((r) => r.data),
    enabled: !!id,
  })

  const { data: members = [] } = useQuery<MemberDetail[]>({
    queryKey: ['group-members', id],
    queryFn: () =>
      client.get<MemberDetail[]>(`/groups/${id}/members/`).then((r) => r.data),
    enabled: !!id,
  })

  const { data: cycles = [] } = useQuery<GroupCycle[]>({
    queryKey: ['group-cycles', id],
    queryFn: () =>
      client.get<GroupCycle[]>(`/groups/${id}/cycles/`).then((r) => r.data),
    enabled: !!id,
  })

  usePageTitle(group?.name ?? '')

  function copyVA() {
    const acct = group?.virtual_account?.account_number ?? ''
    navigator.clipboard.writeText(acct).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }).catch(() => {
      setCopyFailed(true)
      setTimeout(() => setCopyFailed(false), 2000)
    })
  }

  async function handlePay() {
    const myMembership = members.find((m) => m.user_email === user?.email)
    if (!myMembership) {
      setPayError('Could not find your membership for this group.')
      return
    }
    setPayLoading(true)
    setPayError(null)
    try {
      const res = await client.post<{ checkout_url: string }>('/payments/contributions/checkout/', {
        membership_id: myMembership.id,
      })
      const url = res.data.checkout_url
      if (url) {
        window.open(url, '_blank', 'noopener,noreferrer')
      } else {
        setPayError('No payment link returned. Please try again.')
      }
    } catch (err: unknown) {
      const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
      setPayError(detail ?? 'Could not open payment. Please try again.')
    } finally {
      setPayLoading(false)
    }
  }

  const currentCycle = cycles.find((c) => c.status === 'active') ?? cycles[0]
  const amount = group ? naira(parseFloat(group.contribution_amount)) : '—'
  const pot = group
    ? naira(parseFloat(group.contribution_amount) * group.slot_count)
    : '—'
  const pct = cycles.length && group
    ? Math.round((cycles.filter((c) => c.status === 'completed').length / group.slot_count) * 100)
    : 0

  if (!group) {
    return (
      <div className="flex-1 flex items-center justify-center text-[#6B7268] text-sm">
        Loading…
      </div>
    )
  }

  return (
    <div className="flex flex-col flex-1">
      {/* Green header */}
      <header className="bg-[#1B4332] px-6 pt-6 pb-7 rounded-b-[28px] flex flex-col gap-4">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1.5 text-[#A9C0B2] text-sm font-semibold bg-transparent border-none cursor-pointer self-start"
        >
          <ChevronLeft size={18} strokeWidth={2.5} color="#A9C0B2" aria-hidden="true" />
          Back
        </button>
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-extrabold text-[#F8F5F0] tracking-[-0.4px] m-0">
            {group.name}
          </h1>
          <p className="text-sm text-[#A9C0B2] m-0">
            {amount} {group.frequency} · {group.slot_count} members
          </p>
        </div>
      </header>

      <div className="flex flex-col gap-4 px-5 py-5">
        {/* VA card */}
        <section
          aria-label="Group virtual account"
          className="bg-white border border-[#E8E2D6] rounded-2xl p-[18px] flex flex-col gap-2.5"
        >
          <span className="text-[12px] font-bold text-[#6B7268] uppercase tracking-[0.6px]">
            Pay into your group account
          </span>
          <div className="flex items-center justify-between gap-3">
            <div className="flex flex-col gap-0.5">
              <span className="text-[22px] font-extrabold text-[#1F2A24] tracking-[1px] tabular-nums">
                {group.virtual_account?.account_number.replace(/(\d{4})(\d{4})(\d+)/, '$1 $2 $3') ?? '— — —'}
              </span>
              <span className="text-[13px] text-[#6B7268]">
                {group.virtual_account?.bank_name ?? 'Wema Bank'} · Vilapay / {group.name}
              </span>
            </div>
            <button
              onClick={copyVA}
              className="flex items-center gap-1.5 px-3.5 py-2 rounded-[10px] text-[13px] font-bold border-none cursor-pointer flex-none transition-colors"
              style={{
                background: copyFailed ? '#F3E5C3' : copied ? '#DCE9E1' : '#1B4332',
                color: copyFailed ? '#5C4813' : copied ? '#1B4332' : '#F8F5F0',
              }}
            >
              {copyFailed ? 'Failed' : copied ? 'Copied ✓' : 'Copy'}
            </button>
          </div>
          <div className="bg-[#F3E5C3] rounded-[10px] px-3 py-2.5 text-[13px] text-[#5C4813] leading-relaxed">
            Transfer <b>{amount}</b> before{' '}
            <b>{currentCycle ? new Date(currentCycle.payout_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }) : '—'}</b>{' '}
            to stay on track this round.
          </div>
        </section>

        {/* Pay now button */}
        <div className="flex flex-col items-center gap-3">
          <button
            onClick={handlePay}
            disabled={payLoading}
            className="w-full py-4 bg-[#1B4332] text-[#F8F5F0] rounded-xl text-base font-bold border-none cursor-pointer hover:bg-[#173A2B] transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {payLoading ? 'Opening payment…' : `Pay ${amount} now`}
          </button>
          {payError && (
            <p className="text-[13px] text-[#B4472F] text-center m-0">{payError}</p>
          )}
          <p className="text-[13px] font-semibold text-[#6B7268] m-0">
            Or transfer manually to the account above
          </p>
        </div>

        {/* Cycle progress */}
        <section
          aria-label="Cycle progress"
          className="bg-white border border-[#E8E2D6] rounded-2xl p-[18px] flex flex-col gap-3"
        >
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-[#1F2A24]">Cycle progress</span>
            <span className="text-[13px] font-semibold text-[#6B7268]">
              Round {cycles.filter((c) => c.status === 'completed').length} of {group.slot_count}
            </span>
          </div>
          <div className="h-2 bg-[#EFEBE2] rounded-full overflow-hidden" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
            <div className="h-full bg-[#1B4332] rounded-full transition-all" style={{ width: `${pct}%` }} />
          </div>
          <div className="flex justify-between">
            <span className="text-[13px] text-[#6B7268]">
              Pot per round: <b className="text-[#1F2A24]">{pot}</b>
            </span>
          </div>
        </section>

        {/* Members */}
        <section aria-label="Members" className="bg-white border border-[#E8E2D6] rounded-2xl p-[18px]">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-bold text-[#1F2A24]">Members</span>
            <span className="text-[13px] text-[#6B7268]">{members.length} of {group.slot_count}</span>
          </div>
          <ul className="list-none p-0 m-0">
            {members.map((m, i) => {
              const palette = avatarPalette[i % avatarPalette.length]
              return (
                <li
                  key={m.id}
                  className="flex items-center gap-3 py-2 border-b border-[#F1EDE4] last:border-0"
                >
                  <div
                    className="w-9 h-9 rounded-full flex items-center justify-center text-[13px] font-bold flex-none"
                    style={{ background: palette.bg, color: palette.color }}
                    aria-hidden="true"
                  >
                    {initials(m.user_name)}
                  </div>
                  <span className="flex-1 text-sm font-semibold text-[#1F2A24] min-w-0 truncate">
                    {m.user_name}
                  </span>
                  <span className="text-[12px] font-bold px-2.5 py-1 rounded-full text-[#1B4332] bg-[#DCE9E1] flex-none">
                    Slot {m.slot_number}
                  </span>
                </li>
              )
            })}
          </ul>
        </section>

        {/* Payout schedule */}
        {cycles.length > 0 && (
          <section aria-label="Payout schedule" className="bg-white border border-[#E8E2D6] rounded-2xl p-[18px]">
            <span className="text-sm font-bold text-[#1F2A24] block mb-2">Payout schedule</span>
            <ul className="list-none p-0 m-0 flex flex-col gap-0.5">
              {cycles.map((c) => {
                const done = c.status === 'completed'
                const active = c.status === 'active'
                return (
                  <li
                    key={c.id}
                    className="flex items-center gap-3 px-2.5 py-2 rounded-[10px]"
                    style={{ background: active ? '#F3E5C3' : 'transparent' }}
                  >
                    <span
                      className="w-2.5 h-2.5 rounded-full flex-none"
                      style={{ background: done ? '#1B4332' : active ? '#D4A853' : '#DDD6C8' }}
                      aria-hidden="true"
                    />
                    <span className="text-[13px] font-semibold text-[#6B7268] w-14 flex-none">
                      Rd {c.cycle_number}
                    </span>
                    <span
                      className="flex-1 text-sm text-[#1F2A24] min-w-0 truncate"
                      style={{ fontWeight: active ? 700 : 500 }}
                    >
                      {c.recipient_name}
                    </span>
                    <span className="text-[13px] text-[#6B7268] flex-none">
                      {new Date(c.payout_date).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
                    </span>
                  </li>
                )
              })}
            </ul>
          </section>
        )}
      </div>
    </div>
  )
}
