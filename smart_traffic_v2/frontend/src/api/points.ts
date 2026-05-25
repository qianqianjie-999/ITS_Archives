import apiClient from './index'
import type { Point, ParkingEnforcement, Checkpoint } from '@/types'

export interface PointDetail {
  point: Point
  parking_enforcements: ParkingEnforcement[]
  checkpoints: Checkpoint[]
}

export const pointApi = {
  list: () => apiClient.get<Point[]>('/points/'),

  getById: (id: number) => apiClient.get<PointDetail>(`/points/${id}`)
}