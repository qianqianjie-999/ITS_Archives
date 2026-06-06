export function formatDateTime(dateStr: string | undefined | null): string {
  if (!dateStr) return '-'
  
  const date = new Date(dateStr)
  
  if (isNaN(date.getTime())) {
    return dateStr
  }
  
  return date.toLocaleString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

export function formatDate(dateStr: string | undefined | null): string {
  if (!dateStr) return '-'
  
  const date = new Date(dateStr)
  
  if (isNaN(date.getTime())) {
    return dateStr
  }
  
  return date.toLocaleDateString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

export function formatTime(dateStr: string | undefined | null): string {
  if (!dateStr) return '-'
  
  const date = new Date(dateStr)
  
  if (isNaN(date.getTime())) {
    return dateStr
  }
  
  return date.toLocaleTimeString('zh-CN', {
    timeZone: 'Asia/Shanghai',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}