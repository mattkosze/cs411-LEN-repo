// API base URL - uses environment variable if available, defaults to localhost
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Helper to get/set auth token
const AUTH_TOKEN_KEY = 'len_auth_token'

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }
  
  // Add auth token if available
  const token = localStorage.getItem(AUTH_TOKEN_KEY)
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const config = {
    headers,
    ...options,
  }

  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body)
  }

  try {
    const response = await fetch(url, config)
    
    if (!response.ok) {
      // If unauthorized, clear token
      if (response.status === 401) {
        localStorage.removeItem(AUTH_TOKEN_KEY)
      }
      const error = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    //handles empty responses
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
  // Simulated user for development (stores user ID for switching)
  getSimulatedUser: () => {
    return localStorage.getItem('len_simulated_user_id')
  },

  setSimulatedUser: (userId) => {
    localStorage.setItem('len_simulated_user_id', userId.toString())
  },

  clearSimulatedUser: () => {
    localStorage.removeItem('len_simulated_user_id')
  },

  // Authentication endpoints
  register: async (email, password, displayname) => {
    const response = await request('/accounts/register', {
      method: 'POST',
      body: { email, password, displayname },
    })
    if (response.access_token) {
      localStorage.setItem(AUTH_TOKEN_KEY, response.access_token)
    }
    return response
  },

  login: async (email, password) => {
    const response = await request('/accounts/login', {
      method: 'POST',
      body: { email, password },
    })
    if (response.access_token) {
      localStorage.setItem(AUTH_TOKEN_KEY, response.access_token)
    }
    return response
  },

  logout: () => {
    localStorage.removeItem(AUTH_TOKEN_KEY)
    return request('/accounts/logout', {
      method: 'POST',
    })
  },

  isAuthenticated: () => {
    return !!localStorage.getItem(AUTH_TOKEN_KEY)
  },

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

  // Get all users (for dev switcher)
  getUsers: () => {
    return request('/accounts/')
  },

  // Alert mods if crisis
  crisisEscalation: (data) => {
    return request('/crisis/escalate', {
      method: 'POST',
      body: data
    })
  },

  // Report a post
  reportPost: (postId, data) => {
    return request(`/posts/${postId}/report`, {
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

  // Delete own account
  deleteAccount: (reason) => {
    return request('/accounts/me/', {
      method: 'DELETE',
      body: { reason }
    })
  },
  
}

export default api
