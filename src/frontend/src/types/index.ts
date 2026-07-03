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
}

export interface GroupCycle {
  id: string
  cycle_number: number
  status: 'pending' | 'active' | 'completed'
  payout_date: string
  recipient: { id: string; user: { full_name: string }; slot_number: number }
}

export interface Transaction {
  id: string
  amount: string
  transaction_type: 'contribution' | 'payout'
  status: 'pending' | 'success' | 'failed'
  created_at: string
  group_name: string
}

export interface Wallet {
  id: string
  balance: string
  virtual_account_number: string
  bank_name: string
}
