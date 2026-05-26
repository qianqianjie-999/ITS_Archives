import apiClient from './index'
import type { Project } from '@/types'

export const projectApi = {
  list: () => apiClient.get<Project[]>('/projects/'),

  getById: (id: number) => apiClient.get<Project>(`/projects/${id}`),

  create: (data: Partial<Project>) => apiClient.post('/projects/', data),

  update: (id: number, data: Partial<Project>) => apiClient.put(`/projects/${id}`, data),

  delete: (id: number) => apiClient.delete(`/projects/${id}`),

  getByFacility: (facilityType: string, facilityId: number) => {
    const params = { facility_type: facilityType, facility_id: facilityId }
    return apiClient.get<Project[]>('/projects/', { params })
  }
}