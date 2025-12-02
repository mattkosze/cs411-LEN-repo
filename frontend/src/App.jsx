import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { useState, useEffect, useRef } from 'react'
import Home from './pages/Home'
import Board from './pages/Board'
import Account from './pages/Account'
import Moderation from './pages/Moderation'
import { api } from './services/api'
import './App.css'

function App() {
  const [showAccountDropdown, setShowAccountDropdown] = useState(false)
  const [userRole, setUserRole] = useState(null)
  const accountMenuRef = useRef(null)

  useEffect(() => {
    loadUserRole()
  }, [])

  const loadUserRole = async () => {
    try {
      const user = await api.getCurrentUser()
      setUserRole(user?.role || 'user')
    } catch (err) {
      console.error('Error loading user role:', err)
      setUserRole('user')
    }
  }

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (accountMenuRef.current && !accountMenuRef.current.contains(event.target)) {
        setShowAccountDropdown(false)
      }
    }

    if (showAccountDropdown) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showAccountDropdown])

  const isModerator = userRole === 'moderator' || userRole === 'admin'

  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <div className="container header-container">
            <div className="header-left">
              <h1>
                <Link to="/">Len</Link>
              </h1>
            </div>
            <div className="header-right">
              {isModerator && (
                <Link to="/moderation" className="moderation-link">
                  Moderation
                </Link>
              )}
              <div className="account-menu" ref={accountMenuRef}>
                <button 
                  className="account-button"
                  onClick={() => setShowAccountDropdown(!showAccountDropdown)}
                  aria-label="Account menu"
                >
                  Account
                </button>
                {showAccountDropdown && (
                  <div className="account-dropdown">
                    <Link to="/account?tab=profile" onClick={() => setShowAccountDropdown(false)}>
                      View Profile
                    </Link>
                    <Link to="/account?tab=posts" onClick={() => setShowAccountDropdown(false)}>
                      My Posts
                    </Link>
                    <Link to="/account?tab=settings" onClick={() => setShowAccountDropdown(false)}>
                      Settings
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>
        <main className="app-main">
          <div className="container">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/board/:groupId" element={<Board />} />
              <Route path="/account" element={<Account />} />
              <Route path="/moderation" element={<Moderation />} />
            </Routes>
          </div>
        </main>
        <footer className="app-footer">
          <div className="container">
            <p>&copy; 2025 len. A safe space for support and connection.</p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

export default App
