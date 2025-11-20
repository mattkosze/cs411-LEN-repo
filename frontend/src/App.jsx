import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { useState, useEffect, useRef } from 'react'
import Home from './pages/Home'
import Board from './pages/Board'
import Account from './pages/Account'
import './App.css'

function App() {
  const [showAccountDropdown, setShowAccountDropdown] = useState(false)
  const accountMenuRef = useRef(null)

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

  return (
    <Router>
      <div className="app">
        <header className="app-header">
          <div className="container header-container">
            <div className="header-left">
              <h1>
                <Link to="/">len</Link>
              </h1>
            </div>
            <div className="header-right">
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
