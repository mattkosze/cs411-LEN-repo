// Local storage service for managing posts without backend

const STORAGE_KEY = 'len_posts'
const USER_KEY = 'len_current_user'

// Mock current user
const DEFAULT_USER = {
  id: 1,
  display_name: 'Current User',
  isanonymous: false,
  role: 'user'
}

export const storageService = {
  // Get all posts from localStorage
  getPosts: (groupId = null) => {
    try {
      const postsJson = localStorage.getItem(STORAGE_KEY)
      const allPosts = postsJson ? JSON.parse(postsJson) : []
      
      // Filter by group_id if provided
      if (groupId !== null) {
        return allPosts.filter(post => 
          post.group_id === groupId && post.status === 'active'
        )
      }
      
      return allPosts.filter(post => post.status === 'active')
    } catch (error) {
      console.error('Error reading posts from localStorage:', error)
      return []
    }
  },

  // Save a new post
  createPost: (data) => {
    try {
      const postsJson = localStorage.getItem(STORAGE_KEY)
      const allPosts = postsJson ? JSON.parse(postsJson) : []
      
      const currentUser = storageService.getCurrentUser()
      
      const newPost = {
        id: Date.now(), // Simple ID generation
        group_id: data.group_id,
        content: data.content,
        status: 'active',
        createdat: new Date().toISOString(),
        author: {
          id: currentUser.id,
          display_name: currentUser.display_name,
          isanonymous: currentUser.isanonymous,
          role: currentUser.role
        }
      }
      
      allPosts.push(newPost)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(allPosts))
      
      return newPost
    } catch (error) {
      console.error('Error saving post to localStorage:', error)
      throw new Error('Failed to create post')
    }
  },

  // Delete a post
  deletePost: (postId) => {
    try {
      const postsJson = localStorage.getItem(STORAGE_KEY)
      const allPosts = postsJson ? JSON.parse(postsJson) : []
      
      const postIndex = allPosts.findIndex(post => post.id === postId)
      if (postIndex === -1) {
        throw new Error('Post not found')
      }
      
      // Mark as deleted
      allPosts[postIndex].status = 'deleted'
      localStorage.setItem(STORAGE_KEY, JSON.stringify(allPosts))
      
      return { success: true, post_id: postId, status: 'deleted' }
    } catch (error) {
      console.error('Error deleting post from localStorage:', error)
      throw new Error('Failed to delete post')
    }
  },

  // Get current user
  getCurrentUser: () => {
    try {
      const userJson = localStorage.getItem(USER_KEY)
      if (userJson) {
        return JSON.parse(userJson)
      }
      // Set default user if none exists
      localStorage.setItem(USER_KEY, JSON.stringify(DEFAULT_USER))
      return DEFAULT_USER
    } catch (error) {
      console.error('Error reading user from localStorage:', error)
      return DEFAULT_USER
    }
  },

  // Clear all data (useful for testing)
  clearAll: () => {
    localStorage.removeItem(STORAGE_KEY)
    localStorage.removeItem(USER_KEY)
  }
}

