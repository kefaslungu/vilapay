import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { walletApi } from '@/api/wallet'
import { naira } from '@/lib/utils'
import { usePageTitle } from '@/hooks/usePageTitle'
import type { Transaction } from '@/types'

type Filter = 'All' | 'Contributions' | 'Payouts'
const filters: Filter[] = ['All', 'Contributions', 'Payouts']

export default function HistoryPage() {
  usePageTitle('History')
  const [filter, setFilter] = useState<Filter>('All')

  const { data: transactions = [], isLoading } = useQuery({
    queryKey: ['transactions'],
    queryFn: walletApi.transactions,
  })

  const visible = transactions.filter((t: Transaction) => {
    if (filter === 'All') return true
    if (filter === 'Contributions') return t.transaction_type === 'contribution'
    return t.transaction_type === 'payout'
  })

  return (
    <div className="flex flex-col flex-1">
      {/* Green header */}
      <header className="bg-[#1B4332] px-6 pt-6 pb-6 rounded-b-[28px] flex flex-col gap-4">
        <h1 className="text-[22px] font-extrabold text-[#F8F5F0] tracking-[-0.3px] m-0">
          Transactions
        </h1>

        {/* Filter chips */}
        <div className="flex gap-2" role="tablist" aria-label="Transaction filter">
          {filters.map((f) => (
            <button
              key={f}
              role="tab"
              aria-selected={filter === f}
              onClick={() => setFilter(f)}
              className="px-4 py-2 rounded-full text-[13px] font-bold border-none cursor-pointer transition-colors"
              style={{
                background: filter === f ? '#D4A853' : 'rgba(248,245,240,0.14)',
                color: filter === f ? '#1B4332' : '#DCE9E1',
              }}
            >
              {f}
            </button>
          ))}
        </div>
      </header>

      <div className="flex flex-col gap-2.5 px-5 py-5">
        {isLoading && (
          <p className="text-sm text-[#6B7268] text-center py-8">Loading…</p>
        )}

        {!isLoading && visible.length === 0 && (
          <p className="text-sm text-[#6B7268] text-center py-8">No transactions yet.</p>
        )}

        {visible.map((t: Transaction) => {
          const isPayout = t.transaction_type === 'payout'
          return (
            <article
              key={t.id}
              className="bg-white border border-[#E8E2D6] rounded-2xl px-4 py-3.5 flex items-center gap-3.5"
            >
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center flex-none"
                style={{ background: isPayout ? '#DCE9E1' : '#F7E4DE' }}
                aria-hidden="true"
              >
                <span
                  className="text-lg font-extrabold"
                  style={{ color: isPayout ? '#1B7A4B' : '#B4472F' }}
                >
                  {isPayout ? '+' : '−'}
                </span>
              </div>

              <div className="flex flex-col gap-0.5 flex-1 min-w-0">
                <span className="text-[15px] font-bold text-[#1F2A24] truncate">
                  {t.group_name}
                </span>
                <span className="text-[12px] text-[#6B7268]">
                  {isPayout ? 'Payout received' : 'Contribution'} ·{' '}
                  {new Date(t.created_at).toLocaleDateString('en-GB', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric',
                  })}
                </span>
              </div>

              <span
                className="text-[15px] font-extrabold flex-none tabular-nums"
                style={{ color: isPayout ? '#1B7A4B' : '#B4472F' }}
              >
                {isPayout ? '+' : '−'}{naira(parseFloat(t.amount))}
              </span>
            </article>
          )
        })}
      </div>
    </div>
  )
}
