import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

type DRFErrorData = Record<string, string | string[] | number>

/** Extract a human-readable message from a Django REST Framework error response. */
export function parseDrfError(err: unknown, fallback = 'Something went wrong. Please try again.'): string {
  const data = (err as { response?: { data?: DRFErrorData } })?.response?.data
  if (!data) return fallback
  if (typeof data.detail === 'string') return data.detail
  // Collect the first field error message, skipping metadata keys
  for (const [key, val] of Object.entries(data)) {
    if (key === 'status_code') continue
    if (Array.isArray(val) && val.length > 0) return String(val[0])
    if (typeof val === 'string') return val
  }
  return fallback
}

export function naira(amount: number): string {
  return '₦' + Number(amount).toLocaleString('en-NG')
}

export function initials(name: string): string {
  return name
    .split(' ')
    .map((w) => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}
