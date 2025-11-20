const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  }

  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body)
  }

  try {
    const response = await fetch(url, config)
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      return await response.json()
    }
    return null
  } catch (error) {
    console.error('API request failed:', error)
    // Provide more helpful error messages
    if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
      throw new Error('Unable to connect to the server. Please make sure the backend is running on http://localhost:8000')
    }
    throw error
  }
}

export const api = {
  // Get posts, optionally filtered by group_id
  getPosts: (groupId = null) => {
    const params = groupId !== null ? `?group_id=${groupId}` : ''
    return request(`/posts${params}`)
  },

  // Create a new post
  createPost: (data) => {
    return request('/posts/', {
      method: 'POST',
      body: data,
    })
  },

  // Delete a post
  deletePost: (postId) => {
    return request(`/posts/${postId}`, {
      method: 'DELETE',
    })
  },

  // Get current user info
  getCurrentUser: () => {
    return request('/accounts/me')
  },
}

// Condition boards configuration
// In a real app, these would come from the backend
export const CONDITION_BOARDS = [
  { id: 1, name: 'Diabetes', description: 'Support and discussion for diabetes management' },
  { id: 2, name: 'Mental Health', description: 'A safe space for mental health support' },
  { id: 3, name: 'Autoimmune', description: 'Connecting those with autoimmune conditions' },
  { id: 4, name: 'Chronic Pain', description: 'Sharing experiences and coping strategies' },
  { id: 5, name: 'Heart Disease', description: 'Cardiovascular health and support' },
  { id: 6, name: 'Cancer Support', description: 'Supporting each other through treatment' },
  { id: 7, name: 'Arthritis', description: 'Living with arthritis' },
  { id: 8, name: 'Asthma & COPD', description: 'Respiratory health community' },
]

export default api
