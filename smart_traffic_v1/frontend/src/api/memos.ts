import apiClient from './index'
import type { Memo, MemoForm } from '@/types'

export const getMemos = () => {
  return apiClient.get<Memo[]>('/memos')
}

export const getMemo = (id: number) => {
  return apiClient.get<Memo>(`/memos/${id}`)
}

export const createMemo = (data: MemoForm) => {
  return apiClient.post<Memo>('/memos', data)
}

export const updateMemo = (id: number, data: Partial<MemoForm>) => {
  return apiClient.put<Memo>(`/memos/${id}`, data)
}

export const deleteMemo = (id: number) => {
  return apiClient.delete(`/memos/${id}`)
}