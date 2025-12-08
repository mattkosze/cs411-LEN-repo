import { useState } from 'react'
import { api } from '../services/api'
import './Auth.css'

function Auth({ onAuthSuccess }) {
  const [isSignUp, setIsSignUp] = useState(false)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [displayname, setDisplayname] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isSignUp) {
        if (!displayname.trim()) {
          setError('Display name is required')
          setLoading(false)
          return
        }
        await api.register(email, password, displayname)
      } else {
        await api.login(email, password)
      }
      
      // Call success callback to refresh user state
      if (onAuthSuccess) {
        onAuthSuccess()
      }
    } catch (err) {
      setError(err.message || 'An error occurred. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>{isSignUp ? 'Create Account' : 'Sign In'}</h2>
        <p className="auth-subtitle">
          {isSignUp 
            ? 'Join our community to share and connect' 
            : 'Welcome back! Sign in to continue'}
        </p>

        {error && (
          <div className="form-error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {isSignUp && (
            <div className="form-group">
              <label htmlFor="displayname">Display Name</label>
              <input
                id="displayname"
                type="text"
                value={displayname}
                onChange={(e) => setDisplayname(e.target.value)}
                placeholder="Choose a display name"
                required
                maxLength={50}
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your.email@example.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={isSignUp ? "At least 6 characters" : "Enter your password"}
              required
              minLength={isSignUp ? 6 : undefined}
            />
          </div>

          <div className="form-actions">
            <button 
              type="submit" 
              className="btn-primary" 
              disabled={loading}
            >
              {loading ? 'Please wait...' : (isSignUp ? 'Create Account' : 'Sign In')}
            </button>
          </div>
        </form>

        <div className="auth-switch">
          {isSignUp ? (
            <p>
              Already have an account?{' '}
              <button 
                type="button" 
                className="link-button"
                onClick={() => {
                  setIsSignUp(false)
                  setError('')
                }}
              >
                Sign In
              </button>
            </p>
          ) : (
            <p>
              Don't have an account?{' '}
              <button 
                type="button" 
                className="link-button"
                onClick={() => {
                  setIsSignUp(true)
                  setError('')
                }}
              >
                Sign Up
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

export default Auth

