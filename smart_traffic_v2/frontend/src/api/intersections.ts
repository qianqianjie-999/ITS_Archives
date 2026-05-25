import apiClient from './index'
import type { Intersection, TrafficLight, ElectronicPolice } from '@/types'

export interface IntersectionDetail {
  intersection: Intersection
  traffic_lights: TrafficLight[]
  electronic_polices: ElectronicPolice[]
}

export const intersectionApi = {
  list: () => apiClient.get<Intersection[]>('/intersections/'),

  getById: (id: number) => apiClient.get<IntersectionDetail>(`/intersections/${id}`),

  updateTrafficLight: (intersectionId: number, tlId: number, data: Partial<TrafficLight>) =>
    apiClient.put(`/intersections/${intersectionId}/traffic-light/${tlId}`, data),

  updateElectronicPolice: (intersectionId: number, epId: number, data: Partial<ElectronicPolice>) =>
    apiClient.put(`/intersections/${intersectionId}/electronic-police/${epId}`, data),

  extendWarranty: (intersectionId: number, projectName: string, warrantyExpireDate: string) =>
    apiClient.post(`/intersections/${intersectionId}/extend-warranty`, {
      project_name: projectName,
      warranty_expire_date: warrantyExpireDate
    })
}