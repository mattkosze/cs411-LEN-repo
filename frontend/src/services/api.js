// Use environment variable or default to localhost:8000
// If VITE_API_URL is not set, use direct connection (CORS enabled)
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
    console.error('Request URL was:', url)
    // Provide more helpful error messages
    if (error.message === 'Failed to fetch' || error.name === 'TypeError' || error.message.includes('fetch')) {
      const errorMsg = `Unable to connect to the server at ${API_BASE_URL}${endpoint}. ` +
        `Please make sure the backend is running on http://localhost:8000. ` +
        `Error: ${error.message}`
      throw new Error(errorMsg)
    }
    throw error
  }
}

export const api = {
  // Get posts, optionally filtered by group_id
  getPosts: (groupId = null) => {
    const params = groupId !== null ? `?group_id=${groupId}` : ''
    return request(`/posts/${params}`)
  },

  // Get condition boards
  getBoards: () => {
    return request('/boards/')
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
    return request('/accounts/me/')
  },

  // Alert mods if crisis
  crisisEscalation: (data) => {
    return request('/crisis/escalate', {
      method: 'POST',
      body: data
    })
  },

  // Moderation endpoints (moderator only)
  getReports: (status = null) => {
    const params = status ? `?status=${status}` : ''
    return request(`/moderation/reports${params}`)
  },

  determineAction: (data) => {
    return request('/moderation/determine-action', {
      method: 'POST',
      body: data
    })
  },

  deletePostAsModerator: (postId, reason) => {
    return request(`/moderation/delete-post/${postId}?reason=${encodeURIComponent(reason)}`, {
      method: 'POST'
    })
  },

  deleteAccountAsModerator: (userId, reason) => {
    return request(`/moderation/delete-account/${userId}?reason=${encodeURIComponent(reason)}`, {
      method: 'DELETE'
    })
  },
  
}

export default api
