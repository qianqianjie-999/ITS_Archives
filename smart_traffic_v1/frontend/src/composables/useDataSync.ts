import { eventBus, DataEventType, DataEventPayload } from '@/utils/eventBus'
import { onMounted, onBeforeUnmount } from 'vue'

export interface DataSyncOptions {
  types: DataEventType[]
  onUpdate: (payload: DataEventPayload) => void
  onMountedRefresh?: () => void
}

export function useDataSync(options: DataSyncOptions) {
  const handleDataUpdated = (payload: DataEventPayload) => {
    if (!options.types.includes(payload.type) && payload.type !== 'all') {
      return
    }
    options.onUpdate(payload)
  }

  onMounted(() => {
    eventBus.on('dataUpdated', handleDataUpdated)
    if (options.onMountedRefresh) {
      options.onMountedRefresh()
    }
  })

  onBeforeUnmount(() => {
    eventBus.off('dataUpdated', handleDataUpdated)
  })

  return {
    triggerUpdate: (type: DataEventType, action?: 'create' | 'update' | 'delete', id?: number) => {
      eventBus.emit('dataUpdated', type, action, id)
    }
  }
}

export function triggerDataUpdate(type: DataEventType, action?: 'create' | 'update' | 'delete', id?: number) {
  eventBus.emit('dataUpdated', type, action, id)
}
