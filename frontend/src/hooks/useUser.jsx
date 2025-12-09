import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { api } from '../services/api'

/**
 * UserContext provides centralized user state management.
 * 
 * This follows the React Context pattern to avoid prop drilling and
 * duplicated user fetching logic across components.
 */
const UserContext = createContext(null)

export function UserProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  const checkAuth = useCallback(async () => {
    setIsLoading(true)
    const hasToken = api.isAuthenticated()
    
    if (hasToken) {
      try {
        const userData = await api.getCurrentUser()
        setUser(userData)
        setIsAuthenticated(true)
      } catch (err) {
        // Token invalid, clear it
        api.logout()
        setUser(null)
        setIsAuthenticated(false)
      }
    } else {
      setUser(null)
      setIsAuthenticated(false)
    }
    setIsLoading(false)
  }, [])

  const refreshUser = useCallback(async () => {
    if (!api.isAuthenticated()) return
    
    try {
      const userData = await api.getCurrentUser()
      setUser(userData)
    } catch (err) {
      console.error('Error refreshing user:', err)
    }
  }, [])

  const logout = useCallback(async () => {
    try {
      await api.logout()
    } catch (err) {
      console.error('Error during logout:', err)
    }
    setUser(null)
    setIsAuthenticated(false)
  }, [])

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  const value = {
    user,
    isAuthenticated,
    isLoading,
    isModerator: user?.role === 'moderator' || user?.role === 'admin',
    checkAuth,
    refreshUser,
    logout,
  }

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  )
}

/**
 * Hook to access user context.
 * 
 * @returns {Object} User context with user data and auth functions
 * @throws {Error} If used outside of UserProvider
 */
export function useUser() {
  const context = useContext(UserContext)
  if (!context) {
    throw new Error('useUser must be used within a UserProvider')
  }
  return context
}

export default UserContext
