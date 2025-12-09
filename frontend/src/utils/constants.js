/**
 * Shared constants and utilities for the LEN frontend application.
 * 
 * These constants are used across multiple components to ensure consistency
 * and centralize configuration that may need to be updated.
 */

// Crisis detection keywords
// These keywords trigger automatic crisis escalation when detected in posts.
// Keep in sync with backend app/constants.py for server-side validation.
export const CRISIS_KEYWORDS = [
  'end it all',
  'ending it',
  'kill myself',
  'going through it',
  'feeling down',
  'not feeling good',
  'suicide',
  'suicidal',
  'want to die',
  'harm myself',
];

/**
 * Check if content contains crisis-indicating keywords.
 * 
 * @param {string} content - The text content to analyze.
 * @returns {boolean} True if any crisis keyword is found, False otherwise.
 */
export function detectCrisis(content) {
  const contentLower = content.toLowerCase();
  return CRISIS_KEYWORDS.some(keyword => contentLower.includes(keyword));
}

/**
 * Format a timestamp for display.
 * Returns relative time for recent dates, absolute date for older ones.
 * 
 * @param {number} timestamp - Unix timestamp in milliseconds or seconds
 * @param {number} now - Current time in milliseconds (optional, defaults to Date.now())
 * @returns {string} Formatted date string
 */
export function formatRelativeDate(timestamp, now = Date.now()) {
  // Handle both millisecond and second timestamps
  const date = timestamp > 1e12 ? new Date(timestamp) : new Date(timestamp * 1000);
  const diffMs = now - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins} ${diffMins === 1 ? 'minute' : 'minutes'} ago`;
  if (diffHours < 24) return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`;
  if (diffDays < 7) return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`;
  
  return date.toLocaleDateString();
}

/**
 * Format a timestamp for display with time.
 * 
 * @param {number} timestamp - Unix timestamp in milliseconds or seconds
 * @returns {string} Formatted date and time string
 */
export function formatDateTime(timestamp) {
  // Handle both millisecond and second timestamps
  const date = timestamp > 1e12 ? new Date(timestamp) : new Date(timestamp * 1000);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}
