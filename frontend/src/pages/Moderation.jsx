import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { formatDateTime } from '../utils/constants'
import './Moderation.css'

function Moderation() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [statusFilter, setStatusFilter] = useState('open')
  const [selectedReport, setSelectedReport] = useState(null)
  const [selectedAction, setSelectedAction] = useState(null)
  const [actionReason, setActionReason] = useState('')
  const [deletePostReason, setDeletePostReason] = useState('')
  const [deleteAccountReason, setDeleteAccountReason] = useState('')
  const [showDeletePostModal, setShowDeletePostModal] = useState(false)
  const [showDeleteAccountModal, setShowDeleteAccountModal] = useState(false)
  const [targetPostId, setTargetPostId] = useState(null)
  const [targetAccountId, setTargetAccountId] = useState(null)

  useEffect(() => {
    loadReports()
  }, [statusFilter])

  const loadReports = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.getReports(statusFilter === 'all' ? null : statusFilter)
      setReports(data || [])
    } catch (err) {
      console.error('Error loading reports:', err)
      setError(err.message || 'Failed to load reports')
    } finally {
      setLoading(false)
    }
  }

  const handleDetermineAction = async (reportId, action) => {
    if (!actionReason.trim() && action !== 'dismiss') {
      alert('Please provide a reason for this action')
      return
    }

    try {
      await api.determineAction({
        report_id: reportId,
        action: action,
        mod_note: actionReason || null
      })
      setActionReason('')
      setSelectedReport(null)
      setSelectedAction(null)
      loadReports()
    } catch (err) {
      console.error('Error determining action:', err)
      alert('Failed to process action: ' + (err.message || 'Unknown error'))
    }
  }

  const openActionDialog = (reportId, action) => {
    if (action === 'dismiss') {
      // Dismiss doesn't require a reason, so execute immediately
      handleDetermineAction(reportId, action)
    } else {
      setSelectedReport(reportId)
      setSelectedAction(action)
      setActionReason('')
    }
  }

  const handleDeletePost = async () => {
    if (!deletePostReason.trim()) {
      alert('Please provide a reason for deleting this post')
      return
    }

    try {
      await api.deletePostAsModerator(targetPostId, deletePostReason)
      setDeletePostReason('')
      setShowDeletePostModal(false)
      setTargetPostId(null)
      loadReports()
      alert('Post deleted successfully')
    } catch (err) {
      console.error('Error deleting post:', err)
      alert('Failed to delete post: ' + (err.message || 'Unknown error'))
    }
  }

  const handleDeleteAccount = async () => {
    if (!deleteAccountReason.trim()) {
      alert('Please provide a reason for deleting this account')
      return
    }

    if (!window.confirm('Are you sure you want to delete this account? This action cannot be undone.')) {
      return
    }

    try {
      await api.deleteAccountAsModerator(targetAccountId, deleteAccountReason)
      setDeleteAccountReason('')
      setShowDeleteAccountModal(false)
      setTargetAccountId(null)
      loadReports()
      alert('Account deleted successfully')
    } catch (err) {
      console.error('Error deleting account:', err)
      alert('Failed to delete account: ' + (err.message || 'Unknown error'))
    }
  }

  const openDeletePostModal = (postId) => {
    setTargetPostId(postId)
    setShowDeletePostModal(true)
  }

  const openDeleteAccountModal = (userId) => {
    setTargetAccountId(userId)
    setShowDeleteAccountModal(true)
  }

  if (loading) {
    return (
      <div className="moderation-loading">
        <div className="spinner"></div>
        <p>Loading reports...</p>
      </div>
    )
  }

  return (
    <div className="moderation">
      <div className="moderation-header">
        <Link to="/" className="back-link">← Back to home</Link>
        <h1>Moderation Dashboard</h1>
      </div>

      {error && (
        <div className="error-message">
          <p>Error: {error}</p>
          <button className="btn-secondary" onClick={loadReports}>Try Again</button>
        </div>
      )}

      <div className="moderation-filters">
        <button
          className={`filter-button ${statusFilter === 'all' ? 'active' : ''}`}
          onClick={() => setStatusFilter('all')}
        >
          All Reports
        </button>
        <button
          className={`filter-button ${statusFilter === 'open' ? 'active' : ''}`}
          onClick={() => setStatusFilter('open')}
        >
          Open
        </button>
        <button
          className={`filter-button ${statusFilter === 'resolved' ? 'active' : ''}`}
          onClick={() => setStatusFilter('resolved')}
        >
          Resolved
        </button>
        <button
          className={`filter-button ${statusFilter === 'dismissed' ? 'active' : ''}`}
          onClick={() => setStatusFilter('dismissed')}
        >
          Dismissed
        </button>
      </div>

      {reports.length === 0 ? (
        <div className="empty-state">
          <p>No reports found.</p>
        </div>
      ) : (
        <div className="reports-list">
          {reports.map((report) => (
            <div key={report.id} className="report-card">
              <div className="report-header">
                <div className="report-meta">
                  <span className="report-id">Report #{report.id}</span>
                  <span className={`report-status status-${report.status}`}>
                    {report.status}
                  </span>
                  {report.is_crisis && (
                    <span className="crisis-badge">CRISIS</span>
                  )}
                </div>
                <time className="report-time">
                  {formatDateTime(report.created_at)}
                </time>
              </div>

              <div className="report-content">
                <div className="report-reason">
                  <strong>Reason:</strong>
                  <p>{report.reason}</p>
                </div>

                {report.post_id && (
                  <div className="report-target">
                    <strong>Reported Post:</strong>
                    <div className="target-actions">
                      <span>Post ID: {report.post_id}</span>
                      <button
                        className="btn-danger btn-small"
                        onClick={() => openDeletePostModal(report.post_id)}
                      >
                        Delete Post
                      </button>
                    </div>
                  </div>
                )}

                {report.reported_user_id && (
                  <div className="report-target">
                    <strong>Reported User:</strong>
                    <div className="target-actions">
                      <span>User ID: {report.reported_user_id}</span>
                      <button
                        className="btn-danger btn-small"
                        onClick={() => openDeleteAccountModal(report.reported_user_id)}
                      >
                        Delete Account
                      </button>
                    </div>
                  </div>
                )}

                {report.status === 'open' && (
                  <div className="report-actions">
                    <button
                      className="btn-warn"
                      onClick={() => openActionDialog(report.id, 'warn')}
                    >
                      Warn
                    </button>
                    <button
                      className="btn-danger"
                      onClick={() => openActionDialog(report.id, 'ban')}
                    >
                      Ban
                    </button>
                    <button
                      className="btn-secondary"
                      onClick={() => openActionDialog(report.id, 'dismiss')}
                    >
                      Dismiss
                    </button>
                    {selectedReport === report.id && (
                      <div className="action-reason-input">
                        <textarea
                          placeholder={`Enter reason for ${selectedAction} action`}
                          value={actionReason}
                          onChange={(e) => setActionReason(e.target.value)}
                          rows="3"
                        />
                        <div className="action-buttons">
                          <button
                            className="btn-primary"
                            onClick={() => handleDetermineAction(report.id, selectedAction)}
                          >
                            Confirm {selectedAction}
                          </button>
                          <button
                            className="btn-secondary"
                            onClick={() => {
                              setSelectedReport(null)
                              setSelectedAction(null)
                              setActionReason('')
                            }}
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {report.resolution_impact && (
                  <div className="report-resolution">
                    <strong>Resolution:</strong> {report.resolution_impact}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Delete Post Modal */}
      {showDeletePostModal && (
        <div className="modal-overlay" onClick={() => setShowDeletePostModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Delete Post</h2>
            <p>Are you sure you want to delete post #{targetPostId}?</p>
            <textarea
              placeholder="Enter reason for deletion"
              value={deletePostReason}
              onChange={(e) => setDeletePostReason(e.target.value)}
              rows="4"
              className="modal-textarea"
            />
            <div className="modal-actions">
              <button className="btn-danger" onClick={handleDeletePost}>
                Delete Post
              </button>
              <button
                className="btn-secondary"
                onClick={() => {
                  setShowDeletePostModal(false)
                  setDeletePostReason('')
                  setTargetPostId(null)
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Account Modal */}
      {showDeleteAccountModal && (
        <div className="modal-overlay" onClick={() => setShowDeleteAccountModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Delete Account</h2>
            <p>Are you sure you want to delete account #{targetAccountId}? This action cannot be undone.</p>
            <textarea
              placeholder="Enter reason for account deletion"
              value={deleteAccountReason}
              onChange={(e) => setDeleteAccountReason(e.target.value)}
              rows="4"
              className="modal-textarea"
            />
            <div className="modal-actions">
              <button className="btn-danger" onClick={handleDeleteAccount}>
                Delete Account
              </button>
              <button
                className="btn-secondary"
                onClick={() => {
                  setShowDeleteAccountModal(false)
                  setDeleteAccountReason('')
                  setTargetAccountId(null)
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Moderation

