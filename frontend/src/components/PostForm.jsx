import { useState } from 'react'
import { storageService } from '../services/localStorage'
import './PostForm.css'

function PostForm({ groupId, onPostCreated, onCancel }) {
  const [content, setContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!content.trim()) {
      setError('Please enter some content for your post')
      return
    }

    // Check for "crisis test" phrase (case insensitive)
    if (content.toLowerCase().includes('crisis test')) {
      alert('moderators have been alerted')
    }

    setLoading(true)
    setError(null)

    try {
      const newPost = storageService.createPost({
        group_id: groupId,
        content: content.trim(),
      })
      setContent('')
      onPostCreated(newPost)
    } catch (err) {
      console.error('Error creating post:', err)
      setError(err.message || 'Failed to create post. Please try again.')
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
