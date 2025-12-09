/**
 * Shared constants for the LEN frontend application.
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
