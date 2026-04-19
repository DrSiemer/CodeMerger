/**
 * Shared color utility functions for determining contrast and visibility.
 *
 * Returns '#000000' (dark) or '#FFFFFF' (light) based on the input hex color's luminance.
 * Uses the standard W3C relative luminance coefficients.
 */
export const getContrastColor = (hex) => {
  if (!hex || typeof hex !== 'string') return '#FFFFFF'

  try {
    const h = hex.replace('#', '')
    const r = parseInt(h.substring(0, 2), 16)
    const g = parseInt(h.substring(2, 4), 16)
    const b = parseInt(h.substring(4, 6), 16)

    // Relative luminance formula
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b)
    return luminance > 150 ? '#000000' : '#FFFFFF'
  } catch (e) {
    return '#FFFFFF'
  }
}

/**
 * Returns 'dark' or 'light' string identifiers for CSS class mapping.
 */
export const getLuminanceMode = (hex) => {
  const contrast = getContrastColor(hex)
  return contrast === '#000000' ? 'dark' : 'light'
}