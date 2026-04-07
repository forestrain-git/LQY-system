export function formatNumber(num: number, decimals: number = 1): string {
  return num.toFixed(decimals)
}

export function formatTemperature(value: number): string {
  return `${value.toFixed(1)}°C`
}

export function formatVibration(value: number): string {
  return `${value.toFixed(2)}mm/s`
}

export function formatCurrent(value: number): string {
  return `${value.toFixed(1)}A`
}
