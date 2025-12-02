import { useState, useEffect } from 'react'
import { api } from '../services/api'
import './UserSwitcher.css'

function UserSwitcher() {
  const [users, setUsers] = useState([])
  const [currentUser, setCurrentUser] = useState(null)
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      const allUsers = await api.getUsers()
      setUsers(allUsers || [])
      
      // Check for currently selected user
      const savedId = api.getSimulatedUser()
      if (savedId) {
        const found = allUsers.find(u => u.id === parseInt(savedId))
        if (found) setCurrentUser(found)
      } else if (allUsers.length > 0) {
        // Default to first user if none selected (matches backend behavior)
        setCurrentUser(allUsers[0])
      }
    } catch (err) {
      console.error('Failed to load users for switcher:', err)
    }
  }

  const handleUserSelect = (user) => {
    api.setSimulatedUser(user.id)
    setCurrentUser(user)
    setIsOpen(false)
    // Reload page to refresh all data with new user context
    window.location.reload()
  }

  if (users.length === 0) return null

  return (
    <div className="user-switcher">
      <button 
        className="switcher-toggle" 
        onClick={() => setIsOpen(!isOpen)}
        title="Switch User (Dev Tool)"
      >
        <span className="user-role-badge" data-role={currentUser?.role}>
          {currentUser?.role || 'user'}
        </span>
        <span className="user-name">
          {currentUser?.displayname || 'Guest'}
        </span>
        <span className="arrow">▼</span>
      </button>

      {isOpen && (
        <div className="switcher-dropdown">
          <div className="switcher-header">Switch User Perspective</div>
          <div className="switcher-list">
            {users.map(user => (
              <button
                key={user.id}
                className={`switcher-item ${currentUser?.id === user.id ? 'active' : ''}`}
                onClick={() => handleUserSelect(user)}
              >
                <div className="user-info">
                  <span className="name">{user.displayname}</span>
                  <span className="email">{user.email}</span>
                </div>
                <span className="role-badge" data-role={user.role}>
                  {user.role}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default UserSwitcher
