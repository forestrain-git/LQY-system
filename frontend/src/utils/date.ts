import dayjs from 'dayjs'

export function formatDateTime(date: string | Date): string {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

export function formatTime(date: string | Date): string {
  return dayjs(date).format('HH:mm:ss')
}

export function formatDate(date: string | Date): string {
  return dayjs(date).format('YYYY-MM-DD')
}

export function timeAgo(date: string | Date): string {
  return dayjs(date).fromNow()
}

export function duration(start: string | Date, end: string | Date): string {
  const startTime = dayjs(start)
  const endTime = dayjs(end)
  const diff = endTime.diff(startTime, 'second')
  
  if (diff < 60) return `${diff}秒`
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟`
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时`
  return `${Math.floor(diff / 86400)}天`
}
