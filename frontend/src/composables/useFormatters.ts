export const useFormatters = () => {
  const formatKeyToLabel = (key: string): string => {
    if (!key) return ''
    
    // Replace underscores with spaces
    const withSpaces = key.replace(/_/g, ' ')
    
    // Convert to title case (capitalize first letter of each word)
    return withSpaces
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(' ')
  }

  const formatCurrency = (value: number | null | undefined, currency: string = 'USD') => {
    if (value == null) return 'N/A'
    return new Intl.NumberFormat('en-US', { style: 'currency', currency }).format(value)
  }

  const formatNumber = (value: number | null | undefined) => {
    if (value == null) return 'N/A'
    return new Intl.NumberFormat('en-US').format(value)
  }

  const formatLargeNumber = (value: number | null | undefined) => {
    if (value == null) return 'N/A'
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`
    return formatCurrency(value)
  }

  const formatPercent = (value: number | null | undefined) => {
    if (value == null) return 'N/A'
    return `${((value * 100)/100).toFixed(2)}%`
  }

  const formatDecimal = (value: number | null | undefined, decimals: number = 2) => {
    if (value == null) return 'N/A'
    return value.toFixed(decimals)
  }

  return {
    formatKeyToLabel,
    formatCurrency,
    formatNumber,
    formatLargeNumber,
    formatPercent,
    formatDecimal
  }
}
