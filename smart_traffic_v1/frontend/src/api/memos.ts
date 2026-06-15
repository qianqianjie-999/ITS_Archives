import apiClient from './index'
import type { Memo, MemoForm, MemoListResponse } from '@/types'

export interface MemoListParams {
  keyword?: string
  create_user?: string
  start_date?: string
  end_date?: string
  page?: number
  per_page?: number
}

export const getMemos = (params?: MemoListParams): Promise<MemoListResponse> => {
  return apiClient.get('/memos', { params })
}

export const getMemo = (id: number): Promise<Memo> => {
  return apiClient.get(`/memos/${id}`)
}

export const createMemo = (data: MemoForm, files?: File[]): Promise<Memo> => {
  const formData = new FormData()
  formData.append('title', data.title)
  formData.append('content', data.content || '')
  formData.append('happen_time', data.happen_time || '')
  formData.append('create_user', data.create_user)
  
  if (files) {
    for (const file of files) {
      formData.append('files', file)
    }
  }
  
  return apiClient.post('/memos', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const updateMemo = (id: number, data: MemoForm, files?: File[]): Promise<Memo> => {
  const formData = new FormData()
  formData.append('title', data.title)
  formData.append('content', data.content || '')
  formData.append('happen_time', data.happen_time || '')
  formData.append('create_user', data.create_user)
  
  if (files) {
    for (const file of files) {
      formData.append('files', file)
    }
  }
  
  return apiClient.put(`/memos/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const deleteMemo = (id: number): Promise<any> => {
  return apiClient.delete(`/memos/${id}`)
}

export const deleteAttachment = (memoId: number, aid: number): Promise<any> => {
  return apiClient.delete(`/memos/${memoId}/attachments/${aid}`)
}

export const downloadAttachment = (filename: string, originalName: string) => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  const url = `/api/memos/attachments/${filename}?token=${token}`
  const a = document.createElement('a')
  a.href = url
  a.download = originalName
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

export const previewAttachment = (filename: string) => {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token')
  const url = `/api/memos/attachments/${filename}/preview?token=${token}`
  window.open(url, '_blank')
}