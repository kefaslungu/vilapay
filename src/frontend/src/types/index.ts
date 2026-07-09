export interface User {
  id: string
  full_name: string
  email: string
  phone: string
}

export interface Group {
  id: string
  name: string
  slot_count: number
  contribution_amount: string
  frequency: 'daily' | 'weekly' | 'monthly'
  status: 'pending' | 'active' | 'completed'
  invite_code: string
  created_at: string
}

export interface GroupMembership {
  id: string
  group: Group
  slot_number: number
  status: 'active' | 'inactive'
  joined_at: string
  next_payout_date: string | null
}

export interface GroupCycle {
  id: string
  cycle_number: number
  recipient_slot: number
  recipient_name: string
  start_date: string
  end_date: string
  payout_date: string
  status: 'pending' | 'active' | 'completed'
  total_collected: string
}

export interface Transaction {
  id: string
  amount: string
  transaction_type: 'contribution' | 'payout'
  status: 'pending' | 'success' | 'failed'
  created_at: string
  group_name: string
}

export interface WalletSummary {
  balance: string
  wallet_count: number
}
