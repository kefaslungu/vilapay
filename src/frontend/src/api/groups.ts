import client from './client'
import type { Group, GroupMembership } from '@/types'

export const groupsApi = {
  myMemberships: () =>
    client.get<GroupMembership[]>('/groups/memberships/').then((r) => r.data),

  detail: (id: string) =>
    client.get<Group>(`/groups/${id}/`).then((r) => r.data),

  create: (data: {
    name: string
    slot_count: number
    contribution_amount: number
    frequency: string
    start_date: string
  }) => client.post<Group>('/groups/', data).then((r) => r.data),

  joinByCode: (invite_code: string, slot_number?: number) =>
    client
      .post<GroupMembership>('/groups/join-by-code/', { invite_code, slot_number })
      .then((r) => r.data),
}
