import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../services/api'
import PostForm from '../components/PostForm'
import './Board.css'

function Board() {
  const { groupId } = useParams()
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showPostForm, setShowPostForm] = useState(false)
  const [currentUserId, setCurrentUserId] = useState(null)
  const [currentUserRole, setCurrentUserRole] = useState(null)
  // Track current time to allow relative timestamps to update without refetching
  const [now, setNow] = useState(Date.now())
  const [board, setBoard] = useState(null)
  const [boardLoading, setBoardLoading] = useState(true)

  useEffect(() => {
    loadPosts()
    loadCurrentUser()
    loadBoard()
  }, [groupId])

  const loadBoard = async () => {
    setBoardLoading(true)
    try {
      const boards = await api.getBoards()
      const found = boards.find(b => b.id === parseInt(groupId))
      setBoard(found || null)
    } catch (err) {
      console.error('Error loading board info:', err)
      setBoard(null)
    } finally {
      setBoardLoading(false)
    }
  }

  // Updates the post timestamp every minute
  useEffect(() => {
    const interval = setInterval(() => {
      setNow(Date.now())
    }, 60000) // change in 60k increments representing 1 min each
    return () => clearInterval(interval)
  }, [])

  const loadCurrentUser = async () => {
    try {
      const user = await api.getCurrentUser()
      setCurrentUserId(user?.id || null)
      setCurrentUserRole(user?.role || 'user')
    } catch (err) {
      console.error('Error loading current user:', err)
      setCurrentUserId(1) // Fallback user ID if it cannot be retrived
      setCurrentUserRole('user')
    }
  }

  const loadPosts = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getPosts(parseInt(groupId))
      // Sort by created date, newest first (createdat is already a timestamp)
      const sorted = (data || []).sort((a, b) => (b.createdat || 0) - (a.createdat || 0))
      setPosts(sorted)
    } catch (err) {
      console.error('Error loading posts:', err)
      setError(err.message || 'Failed to load posts')
      setPosts([])
    } finally {
      setLoading(false)
    }
  }

  const handlePostCreated = () => {
    // Reload from the database to get the latest posts
    loadPosts()
    setShowPostForm(false)
  }

  const handleDeletePost = async (postId) => {
    const isModerator = currentUserRole === 'moderator' || currentUserRole === 'admin'
    
    if (isModerator) {
      const reason = prompt('Enter reason for deletion (required for moderators):')
      if (!reason || !reason.trim()) {
        alert('Reason is required for moderator deletions')
        return
      }
      if (!window.confirm('Are you sure you want to delete this post as a moderator?')) {
        return
      }
      try {
        await api.deletePostAsModerator(postId, reason)
        loadPosts()
      } catch (err) {
        console.error('Error deleting post:', err)
        alert('Failed to delete post: ' + (err.message || 'Unknown error'))
      }
    } else {
      if (!window.confirm('Are you sure you want to delete this post?')) {
        return
      }
      try {
        await api.deletePost(postId)
        loadPosts()
      } catch (err) {
        console.error('Error deleting post:', err)
        alert('Failed to delete post: ' + (err.message || 'Unknown error'))
      }
    }
  }

  const formatDate = (timestamp) => {
    // Handle both timestamp (number) and Date object
    const date = typeof timestamp === 'number' ? new Date(timestamp) : timestamp
    const diffMs = now - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins} ${diffMins === 1 ? 'minute' : 'minutes'} ago`
    if (diffHours < 24) return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`
    if (diffDays < 7) return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`
    return date.toLocaleDateString()
  }

  // Show loading state while board is being loaded
  if (boardLoading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading board...</p>
      </div>
    )
  }

  // Show error if board not found after loading
  if (!board) {
    return (
      <div className="board-error">
        <h2>Board not found</h2>
        <p>The requested board does not exist.</p>
        <Link to="/" className="btn-primary">Back to Home</Link>
      </div>
    )
  }

  return (
    <div className="board">
      <div className="board-header">
        <Link to="/" className="back-link">← Back to boards</Link>
        <div className="board-title-section">
          <div>
            <h1>{board.name}</h1>
          </div>
        </div>
        <button
          className="btn-primary"
          onClick={() => setShowPostForm(!showPostForm)}
        >
          {showPostForm ? 'Cancel' : '+ New Post'}
        </button>
      </div>

      {showPostForm && (
        <div className="post-form-container">
          <PostForm
            groupId={parseInt(groupId)}
            onPostCreated={handlePostCreated}
            onCancel={() => setShowPostForm(false)}
          />
        </div>
      )}

      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading posts...</p>
        </div>
      ) : error ? (
        <div className="error-message">
          <p>Error: {error}</p>
          <button className="btn-secondary" onClick={loadPosts}>Try Again</button>
        </div>
      ) : posts.length === 0 ? (
        <div className="empty-state">
          <p>No posts yet. Be the first to share something!</p>
        </div>
      ) : (
        <div className="posts-list">
          {posts.map((post) => (
            <article key={post.id} className="post-card">
              <div className="post-header">
                <div className="post-author">
                  <span className="author-name">
                    {post.author.isanonymous ? 'Anonymous' : post.author.displayname}
                  </span>
                </div>
                <time className="post-time" dateTime={post.createdat}>
                  {formatDate(post.createdat)}
                </time>
              </div>
              <div className="post-content">
                {post.content.split('\n').map((paragraph, idx) => (
                  <p key={idx}>{paragraph || '\u00A0'}</p>
                ))}
              </div>
              {post.status !== 'active' && (
                <div className="post-status">
                  Status: <span className={`status-${post.status}`}>{post.status}</span>
                </div>
              )}
              {post.status === 'active' && (
                ((currentUserId && post.author && post.author.id === currentUserId) || 
                 (currentUserRole === 'moderator' || currentUserRole === 'admin')) && (
                  <div className="post-actions">
                    <button
                      className="btn-delete"
                      onClick={() => handleDeletePost(post.id)}
                      aria-label="Delete post"
                    >
                      {(currentUserRole === 'moderator' || currentUserRole === 'admin') && 
                       (!post.author || post.author.id !== currentUserId) 
                        ? 'Delete (Mod)' 
                        : 'Delete'}
                    </button>
                  </div>
                )
              )}
            </article>
          ))}
        </div>
      )}
    </div>
  )
}

export default Board
