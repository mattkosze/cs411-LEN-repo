import { useState } from 'react'
import { api } from "../services/api" 
import { detectCrisis } from '../utils/constants'
import './PostForm.css'

function PostForm({ groupId, onPostCreated, onCancel }) {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Disallow empty messages
    if (!content.trim()) {
      setError('Please enter some content for your post')
      return
    }

    // Check for crisis keywords using centralized utility
    const isCrisis = detectCrisis(content)
    
    if (isCrisis) {
      alert('Crisis detected. Moderators have been alerted and support resources are being prepared.')
      try {
        await api.crisisEscalation({
          content_snip: content        
        })
      } catch (err) {
        console.error('Error escalating crisis:', err)
      }
    }

    setLoading(true)
    setError(null)
    try {
      await api.createPost({
        group_id: groupId,
        content: content.trim(),
        posttime: Date.now()
      })
      setContent('')
      onPostCreated()
    } catch (err) {
      console.error('Error creating post:', err)
      setError(err.message || 'Failed to create post. Please try again or come back soon.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="post-form" onSubmit={handleSubmit}>
      <h3>Create a New Post</h3>
      
      {error && (
        <div className="form-error">
          {error}
        </div>
      )}

      <div className="form-group">
        <label htmlFor="content">Share your thoughts or experiences:</label>
        <textarea
          id="content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Write your post here..."
          rows={8}
          disabled={loading}
          required
        />
        <div className="char-count">
          {content.length} characters
        </div>
      </div>

      <div className="form-actions">
        <button
          type="button"
          className="btn-secondary"
          onClick={onCancel}
          disabled={loading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="btn-primary"
          disabled={loading || !content.trim()}
        >
          {loading ? 'Posting...' : 'Post'}
        </button>
      </div>
    </form>
  )
}

export default PostForm
