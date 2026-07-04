import { useEffect } from 'react'

export function usePageTitle(title: string) {
  useEffect(() => {
    document.title = title ? `${title} | Vilapay` : 'Vilapay'
    return () => {
      document.title = 'Vilapay'
    }
  }, [title])
}
