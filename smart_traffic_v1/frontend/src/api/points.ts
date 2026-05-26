import apiClient from './index'
import type { Point, ParkingEnforcement, Checkpoint } from '@/types'

export interface PointDetail {
  point: Point
  parking_enforcements: ParkingEnforcement[]
  checkpoints: Checkpoint[]
}

export const pointApi = {
  list: () => apiClient.get<Point[]>('/points/'),

  create: (data: Partial<Point>) => apiClient.post('/points/', data),

  getById: (id: number) => apiClient.get<PointDetail>(`/points/${id}`),

  update: (id: number, data: Partial<Point>) => apiClient.put(`/points/${id}`, data),

  delete: (id: number) => apiClient.delete(`/points/${id}`),

  updateParkingEnforcement: (pointId: number, peId: number, data: Partial<ParkingEnforcement>) =>
    apiClient.put(`/points/${pointId}/parking-enforcement/${peId}`, data),

  deleteParkingEnforcement: (pointId: number, peId: number) =>
    apiClient.delete(`/points/${pointId}/parking-enforcement/${peId}`),

  createParkingEnforcement: (pointId: number, data: Partial<ParkingEnforcement>) =>
    apiClient.post(`/points/${pointId}/parking-enforcement`, data),

  updateCheckpoint: (pointId: number, cpId: number, data: Partial<Checkpoint>) =>
    apiClient.put(`/points/${pointId}/checkpoint/${cpId}`, data),

  deleteCheckpoint: (pointId: number, cpId: number) =>
    apiClient.delete(`/points/${pointId}/checkpoint/${cpId}`),

  createCheckpoint: (pointId: number, data: Partial<Checkpoint>) =>
    apiClient.post(`/points/${pointId}/checkpoint`, data),

  extendWarranty: (pointId: number, projectName: string, warrantyExpireDate: string) =>
    apiClient.post(`/points/${pointId}/extend-warranty`, {
      project_name: projectName,
      warranty_expire_date: warrantyExpireDate
    })
}