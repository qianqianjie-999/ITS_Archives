import apiClient from './index'
import type { Intersection, TrafficLight, ElectronicPolice } from '@/types'

export interface IntersectionDetail {
  intersection: Intersection
  traffic_lights: TrafficLight[]
  electronic_polices: ElectronicPolice[]
}

interface PaginatedResponse<T> {
  data: T[]
  page: number
  per_page: number
  total: number
  pages: number
}

export const intersectionApi = {
  list(params?: { page?: number; per_page?: number }): Promise<PaginatedResponse<Intersection>> {
    return apiClient.get('/intersections/', { params })
  },

  create: (data: Partial<Intersection>) => apiClient.post('/intersections/', data),

  getById: (id: number) => apiClient.get<IntersectionDetail>(`/intersections/${id}`),

  update: (id: number, data: Partial<Intersection>) => apiClient.put(`/intersections/${id}`, data),

  delete: (id: number) => apiClient.delete(`/intersections/${id}`),

  getTrafficLightsAll: () => apiClient.get<TrafficLight[]>('/intersections/traffic-lights'),

  getElectronicPolicesAll: () => apiClient.get<ElectronicPolice[]>('/intersections/electronic-polices'),

  createTrafficLight: (intersectionId: number, data: Partial<TrafficLight>) =>
    apiClient.post(`/intersections/${intersectionId}/traffic-light`, data),

  updateTrafficLight: (intersectionId: number, tlId: number, data: Partial<TrafficLight>) =>
    apiClient.put(`/intersections/${intersectionId}/traffic-light/${tlId}`, data),

  deleteTrafficLight: (intersectionId: number, tlId: number) =>
    apiClient.delete(`/intersections/${intersectionId}/traffic-light/${tlId}`),

  createElectronicPolice: (intersectionId: number, data: Partial<ElectronicPolice>) =>
    apiClient.post(`/intersections/${intersectionId}/electronic-police`, data),

  updateElectronicPolice: (intersectionId: number, epId: number, data: Partial<ElectronicPolice>) =>
    apiClient.put(`/intersections/${intersectionId}/electronic-police/${epId}`, data),

  deleteElectronicPolice: (intersectionId: number, epId: number) =>
    apiClient.delete(`/intersections/${intersectionId}/electronic-police/${epId}`),

  extendWarranty: (intersectionId: number, projectId: number, deviceType: string, warrantyExpireDate: string) =>
    apiClient.post(`/intersections/${intersectionId}/extend-warranty`, {
      project_id: projectId,
      device_type: deviceType,
      warranty_expire_date: warrantyExpireDate
    })
}