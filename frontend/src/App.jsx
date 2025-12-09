import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom'
import { useState, useEffect, useRef } from 'react'
import Home from './pages/Home'
import Board from './pages/Board'
import Account from './pages/Account'
import Moderation from './pages/Moderation'
import Auth from './components/Auth'
import { api } from './services/api'
import './App.css'
import logo from './assets/logo.svg'

function AppContent() {
  const [showAccountDropdown, setShowAccountDropdown] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [userRole, setUserRole] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const accountMenuRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    setIsLoading(true)
    const hasToken = api.isAuthenticated()
    if (hasToken) {
      try {
        const user = await api.getCurrentUser()
        setUserRole(user?.role || 'user')
        setIsAuthenticated(true)
      } catch (err) {
        // Token invalid, clear it
        api.logout()
        setIsAuthenticated(false)
        setUserRole(null)
      }
    } else {
      setIsAuthenticated(false)
      setUserRole(null)
    }
    setIsLoading(false)
  }

  const handleAuthSuccess = () => {
    checkAuth()
    navigate('/')
  }

  const handleLogout = async () => {
    try {
      await api.logout()
      setIsAuthenticated(false)
      setUserRole(null)
      setShowAccountDropdown(false)
      navigate('/')
    } catch (err) {
      console.error('Error logging out:', err)
      // Still clear local state even if API call fails
      setIsAuthenticated(false)
      setUserRole(null)
      navigate('/')
    }
  }

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

  if (isLoading) {
    return (
      <div className="app">
        <div className="container" style={{ textAlign: 'center', padding: '4rem 0' }}>
          <p>Loading...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="app">
        <header className="app-header">
          <div className="container header-container">
            <div className="header-left">
              <h1>
                <Link to="/" className="logo-link">
                  <img src={logo} alt="Len Logo" className="app-logo" />
                </Link>
              </h1>
            </div>
          </div>
        </header>
        <main className="app-main">
          <div className="container">
            <Auth onAuthSuccess={handleAuthSuccess} />
          </div>
        </main>
        <footer className="app-footer">
          <div className="container">
            <p>&copy; 2025 len. A safe space for support and connection.</p>
          </div>
        </footer>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="container header-container">
          <div className="header-left">
            <h1>
              <Link to="/" className="logo-link">
                <img src={logo} alt="Len Logo" className="app-logo" />
              </Link>
            </h1>
          </div>
          <button 
            className="mobile-menu-toggle"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            <span className="bar"></span>
            <span className="bar"></span>
            <span className="bar"></span>
          </button>

          <div className={`header-right ${mobileMenuOpen ? 'active' : ''}`}>
            {isModerator && (
              <Link 
                to="/moderation" 
                className="moderation-link"
                onClick={() => setMobileMenuOpen(false)}
              >
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
                  <Link 
                    to="/account?tab=profile" 
                    onClick={() => {
                      setShowAccountDropdown(false)
                      setMobileMenuOpen(false)
                    }}
                  >
                    View Profile
                  </Link>
                  <Link 
                    to="/account?tab=posts" 
                    onClick={() => {
                      setShowAccountDropdown(false)
                      setMobileMenuOpen(false)
                    }}
                  >
                    My Posts
                  </Link>
                  <Link 
                    to="/account?tab=settings" 
                    onClick={() => {
                      setShowAccountDropdown(false)
                      setMobileMenuOpen(false)
                    }}
                  >
                    Settings
                  </Link>
                  <button 
                    className="account-dropdown-button"
                    onClick={handleLogout}
                  >
                    Sign Out
                  </button>
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
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App
