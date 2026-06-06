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

export const getMemos = (params?: MemoListParams) => {
  return apiClient.get<MemoListResponse>('/memos', { params })
}

export const getMemo = (id: number) => {
  return apiClient.get<Memo>(`/memos/${id}`)
}

export const createMemo = (data: MemoForm, files?: FileList) => {
  const formData = new FormData()
  formData.append('title', data.title)
  formData.append('content', data.content || '')
  formData.append('happen_time', data.happen_time || '')
  formData.append('create_user', data.create_user)
  
  if (files) {
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i])
    }
  }
  
  return apiClient.post<Memo>('/memos', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const updateMemo = (id: number, data: MemoForm, files?: FileList) => {
  const formData = new FormData()
  formData.append('title', data.title)
  formData.append('content', data.content || '')
  formData.append('happen_time', data.happen_time || '')
  formData.append('create_user', data.create_user)
  
  if (files) {
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i])
    }
  }
  
  return apiClient.put<Memo>(`/memos/${id}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

export const deleteMemo = (id: number) => {
  return apiClient.delete(`/memos/${id}`)
}

export const deleteAttachment = (memoId: number, aid: number) => {
  return apiClient.delete(`/memos/${memoId}/attachments/${aid}`)
}

export const downloadAttachment = (filename: string, originalName: string) => {
  const url = `/api/memos/attachments/${filename}`
  const a = document.createElement('a')
  a.href = url
  a.download = originalName
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

export const previewAttachment = (filename: string) => {
  const url = `/api/memos/attachments/${filename}/preview`
  window.open(url, '_blank')
}