import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../services/api'
import './Account.css'

function Account() {
  const [userInfo, setUserInfo] = useState(null)
  const [userPosts, setUserPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchParams] = useSearchParams()
  const [activeTab, setActiveTab] = useState(searchParams.get('tab') || 'profile')

  useEffect(() => {
    loadUserData()
  }, [])

  useEffect(() => {
    const tab = searchParams.get('tab')
    if (tab) {
      setActiveTab(tab)
    }
  }, [searchParams])

  const loadUserData = async () => {
    try {
      // Set the User
      const user = await api.getCurrentUser()
      setUserInfo(user)

      // Query posts for the selected user from our DB
      const allPosts = await api.getPosts()
      setUserPosts(allPosts.filter(post => post.author.id === user.id))
    } catch (error) {
      // Log any issues loading data
      console.error('Error loading user data:', error)
    } finally {
      // On success, set loading to false
      setLoading(false)
    }
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString()
  }

  if (loading) {
    return (
      <div className="account-loading">
        <div className="spinner"></div>
        <p>Loading account...</p>
      </div>
    )
  }

  return (
    <div className="account">
      <div className="account-header">
        <Link to="/" className="back-link">← Back to home</Link>
        <h1>Account</h1>
      </div>

      <div className="account-tabs">
        <button
          className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          Profile
        </button>
        <button
          className={`tab-button ${activeTab === 'posts' ? 'active' : ''}`}
          onClick={() => setActiveTab('posts')}
        >
          My Posts
        </button>
        <button
          className={`tab-button ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          Settings
        </button>
      </div>

      <div className="account-content">
        {activeTab === 'profile' && (
          <div className="profile-section">
            <div className="profile-card">
              <h2>Profile Information</h2>
              {userInfo ? (
                <div className="profile-info">
                  <div className="info-row">
                    <label>Display Name:</label>
                    <span>{userInfo.isanonymous ? 'Anonymous' : userInfo.displayname}</span>
                  </div>
                  <div className="info-row">
                    <label>User ID:</label>
                    <span>{userInfo.id}</span>
                  </div>
                  <div className="info-row">
                    <label>Role:</label>
                    <span className={`role-badge role-${userInfo.role}`}>
                      {userInfo.role}
                    </span>
                    {(userInfo.role === 'moderator' || userInfo.role === 'admin') && (
                      <Link to="/moderation" className="moderation-link-inline">
                        Go to Moderation Dashboard →
                      </Link>
                    )}
                  </div>
                  <div className="info-row">
                    <label>Anonymous Mode:</label>
                    <span>{userInfo.isanonymous ? 'Yes' : 'No'}</span>
                  </div>
                </div>
              ) : (
                <p>No profile information available.</p>
              )}
            </div>
          </div>
        )}

        {activeTab === 'posts' && (
          <div className="posts-section">
            <h2>My Posts</h2>
            {userPosts.length === 0 ? (
              <div className="empty-state">
                <p>You haven't made any posts yet.</p>
                <Link to="/" className="btn-primary">Browse Communities</Link>
              </div>
            ) : (
              <div className="user-posts-list">
                {userPosts.map((post) => (
                  <div key={post.id} className="user-post-card">
                    <div className="post-header">
                      <h3>Post #{post.id}</h3>
                      <time>{formatDate(post.createdat)}</time>
                    </div>
                    <div className="post-content-preview">
                      {post.content.substring(0, 150)}
                      {post.content.length > 150 && '...'}
                    </div>
                    <div className="post-status-info">
                      Status: <span className={`status-${post.status}`}>{post.status}</span>
                      {post.group_id && (
                        <Link to={`/board/${post.group_id}`} className="view-post-link">
                          View in Community
                        </Link>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="settings-section">
            <div className="settings-card">
              <h2>Account Settings</h2>
              <div className="settings-list">
                <div className="setting-item">
                  <label>Display Name</label>
                  <input type="text" placeholder="Your display name" defaultValue={userInfo?.displayname || ''} />
                  <p className="setting-hint">This name will be shown on your posts</p>
                </div>
                <div className="setting-item">
                  <label>Anonymous Mode</label>
                  <label className="toggle-switch">
                    <input type="checkbox" defaultChecked={userInfo?.isanonymous || false} />
                    <span className="toggle-slider"></span>
                  </label>
                  <p className="setting-hint">When enabled, your posts will show as anonymous</p>
                </div>
                <div className="setting-item">
                  <button className="btn-danger">Delete Account</button>
                  <p className="setting-hint">Permanently delete your account and anonymize all content</p>
                </div>
              </div>
              <div className="settings-actions">
                <button className="btn-primary">Save Changes</button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Account
