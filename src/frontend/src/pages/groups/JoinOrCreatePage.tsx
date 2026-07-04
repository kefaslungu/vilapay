import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { ChevronLeft } from 'lucide-react'
import { groupsApi } from '@/api/groups'
import { naira } from '@/lib/utils'
import { usePageTitle } from '@/hooks/usePageTitle'

type Tab = 'create' | 'join'

export default function JoinOrCreatePage() {
  usePageTitle('New group')
  const [tab, setTab] = useState<Tab>('create')
  const navigate = useNavigate()
  const qc = useQueryClient()

  // Create form
  const [form, setForm] = useState({
    name: '',
    slots: '10',
    amount: '',
    frequency: 'monthly',
    start_date: new Date().toISOString().slice(0, 10),
  })

  // Join form
  const [code, setCode] = useState('')

  const pot =
    Number(form.amount) > 0 && Number(form.slots) > 0
      ? naira(Number(form.amount) * Number(form.slots))
      : null

  const createMutation = useMutation({
    mutationFn: () =>
      groupsApi.create({
        name: form.name.trim(),
        slot_count: Number(form.slots),
        contribution_amount: Number(form.amount),
        frequency: form.frequency,
        start_date: form.start_date,
      }),
    onSuccess: (group) => {
      qc.invalidateQueries({ queryKey: ['memberships'] })
      navigate(`/groups/${group.id}`, { replace: true })
    },
  })

  const joinMutation = useMutation({
    mutationFn: () => groupsApi.joinByCode(code.trim().toUpperCase()),
    onSuccess: (membership) => {
      qc.invalidateQueries({ queryKey: ['memberships'] })
      navigate(`/groups/${membership.group.id}`, { replace: true })
    },
  })

  function set(key: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value }))
  }

  return (
    <div className="flex flex-col flex-1 px-6 pt-7 pb-6">
      {/* Back */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1.5 text-[#1B4332] text-sm font-semibold bg-transparent border-none cursor-pointer mb-[22px] self-start"
      >
        <ChevronLeft size={18} strokeWidth={2.5} aria-hidden="true" />
        Back
      </button>

      <h1 className="text-2xl font-extrabold text-[#1B4332] tracking-[-0.4px] mb-[18px] m-0">
        Start saving together
      </h1>

      {/* Tabs */}
      <div className="flex bg-[#EFEBE2] rounded-xl p-1 gap-1 mb-[22px]" role="tablist">
        {(['create', 'join'] as Tab[]).map((t) => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            onClick={() => setTab(t)}
            className="flex-1 py-[11px] rounded-[9px] text-sm font-bold border-none cursor-pointer transition-colors"
            style={{
              background: tab === t ? '#1B4332' : 'transparent',
              color: tab === t ? '#F8F5F0' : '#6B7268',
            }}
          >
            {t === 'create' ? 'Create a group' : 'Join with code'}
          </button>
        ))}
      </div>

      {/* Create tab */}
      {tab === 'create' && (
        <form
          onSubmit={(e) => { e.preventDefault(); createMutation.mutate() }}
          className="flex flex-col gap-[14px]"
          noValidate
        >
          <div className="flex flex-col gap-1.5">
            <label htmlFor="name" className="text-[13px] font-semibold text-[#3E4A42]">
              Group name
            </label>
            <input
              id="name"
              type="text"
              placeholder="e.g. Market Women Circle"
              value={form.name}
              onChange={set('name')}
              required
              className="w-full px-4 py-[14px] border border-[#DDD6C8] rounded-xl bg-white text-base text-[#1F2A24] focus:outline-[2px] focus:outline-[#1B4332] focus:outline-offset-0"
            />
          </div>

          <div className="flex gap-3">
            <div className="flex-1 flex flex-col gap-1.5">
              <label htmlFor="slots" className="text-[13px] font-semibold text-[#3E4A42]">
                Slots
              </label>
              <input
                id="slots"
                type="number"
                min={2}
                max={30}
                value={form.slots}
                onChange={set('slots')}
                className="w-full px-4 py-[14px] border border-[#DDD6C8] rounded-xl bg-white text-base text-[#1F2A24] focus:outline-[2px] focus:outline-[#1B4332] focus:outline-offset-0"
              />
            </div>
            <div className="flex-[1.6] flex flex-col gap-1.5">
              <label htmlFor="amount" className="text-[13px] font-semibold text-[#3E4A42]">
                Contribution
              </label>
              <div className="flex items-center bg-white border border-[#DDD6C8] rounded-xl pl-3.5">
                <span className="text-base font-semibold text-[#6B7268]">₦</span>
                <input
                  id="amount"
                  type="number"
                  min={500}
                  step={500}
                  placeholder="25,000"
                  value={form.amount}
                  onChange={set('amount')}
                  className="flex-1 min-w-0 px-2 py-[14px] bg-transparent border-none text-base text-[#1F2A24] focus:outline-none"
                />
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <div className="flex-1 flex flex-col gap-1.5">
              <label htmlFor="frequency" className="text-[13px] font-semibold text-[#3E4A42]">
                Frequency
              </label>
              <select
                id="frequency"
                value={form.frequency}
                onChange={set('frequency')}
                className="w-full px-3 py-[14px] border border-[#DDD6C8] rounded-xl bg-white text-base text-[#1F2A24] focus:outline-[2px] focus:outline-[#1B4332] focus:outline-offset-0"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
            <div className="flex-1 flex flex-col gap-1.5">
              <label htmlFor="start_date" className="text-[13px] font-semibold text-[#3E4A42]">
                Start date
              </label>
              <input
                id="start_date"
                type="date"
                value={form.start_date}
                onChange={set('start_date')}
                className="w-full px-3 py-[13px] border border-[#DDD6C8] rounded-xl bg-white text-[15px] text-[#1F2A24] focus:outline-[2px] focus:outline-[#1B4332] focus:outline-offset-0"
              />
            </div>
          </div>

          {pot && (
            <div className="bg-[#DCE9E1] rounded-xl px-3.5 py-3 text-[13px] text-[#1B4332] leading-relaxed">
              Each member receives <b>{pot}</b> when their turn comes. Full cycle:{' '}
              {form.slots} rounds, {form.frequency}.
            </div>
          )}

          {createMutation.isError && (
            <p role="alert" className="text-sm text-[#B4472F] m-0">
              Failed to create group. Please try again.
            </p>
          )}

          <button
            type="submit"
            disabled={createMutation.isPending}
            className="w-full py-4 bg-[#1B4332] text-[#F8F5F0] rounded-xl text-base font-bold border-none cursor-pointer hover:bg-[#173A2B] transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {createMutation.isPending ? 'Creating…' : 'Create group'}
          </button>
        </form>
      )}

      {/* Join tab */}
      {tab === 'join' && (
        <form
          onSubmit={(e) => { e.preventDefault(); joinMutation.mutate() }}
          className="flex flex-col gap-4"
          noValidate
        >
          <div className="flex flex-col gap-1.5">
            <label htmlFor="invite_code" className="text-[13px] font-semibold text-[#3E4A42]">
              Invite code
            </label>
            <input
              id="invite_code"
              type="text"
              placeholder="VLA-8K2QF9"
              value={code}
              onChange={(e) => setCode(e.target.value.toUpperCase())}
              maxLength={9}
              required
              className="w-full px-4 py-[18px] border border-[#DDD6C8] rounded-xl bg-white text-[20px] font-bold tracking-[2px] text-[#1F2A24] text-center uppercase focus:outline-[2px] focus:outline-[#1B4332] focus:outline-offset-0"
            />
            <span className="text-[13px] text-[#6B7268] leading-relaxed mt-0.5">
              Ask the group admin for their 9-character invite code.
            </span>
          </div>

          {joinMutation.isError && (
            <p role="alert" className="text-sm text-[#B4472F] m-0">
              Invalid invite code. Please check and try again.
            </p>
          )}

          <button
            type="submit"
            disabled={joinMutation.isPending || code.length < 9}
            className="w-full py-4 bg-[#1B4332] text-[#F8F5F0] rounded-xl text-base font-bold border-none cursor-pointer hover:bg-[#173A2B] transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {joinMutation.isPending ? 'Joining…' : 'Join group'}
          </button>
        </form>
      )}
    </div>
  )
}
