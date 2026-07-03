import client from './client'
import type { Wallet, Transaction } from '@/types'

export const walletApi = {
  mine: () => client.get<Wallet>('/wallets/me/').then((r) => r.data),

  transactions: () =>
    client.get<Transaction[]>('/wallets/transactions/').then((r) => r.data),
}
