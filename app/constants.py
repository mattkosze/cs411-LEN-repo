"""
Shared constants for the LEN application.

These constants are used across multiple modules to ensure consistency
and centralize configuration that may need to be updated.
"""

# Crisis detection keywords
# These keywords trigger automatic crisis escalation when detected in posts.
# Keep in sync with frontend/src/utils/constants.js for client-side detection.
CRISIS_KEYWORDS = [
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
]


def detect_crisis(content: str) -> bool:
    """Check if content contains crisis-indicating keywords.
    
    Args:
        content: The text content to analyze.
        
    Returns:
        True if any crisis keyword is found, False otherwise.
    """
    content_lower = content.lower()
    return any(keyword in content_lower for keyword in CRISIS_KEYWORDS)
