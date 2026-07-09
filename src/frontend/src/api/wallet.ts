import client from './client'
import type { WalletSummary, Transaction } from '@/types'

export const walletApi = {
  mine: () => client.get<WalletSummary>('/wallets/me/').then((r) => r.data),

  transactions: () =>
    client.get<Transaction[]>('/wallets/transactions/').then((r) => r.data),
}
