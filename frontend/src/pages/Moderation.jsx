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
                  <span className={`report-reason-tag reason-${report.reason?.toLowerCase().replace(/\s+/g, '-')}`}>
                    {report.reason}
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
                <div className="report-comment">
                  <strong>Reporter Comment:</strong>
                  <p>{
                    // For auto-detected crises, the details are just the post content - show N/A
                    report.is_crisis && report.details && report.post?.content && 
                    report.details.trim().substring(0, 200) === report.post.content.trim().substring(0, 200)
                      ? 'N/A (auto-detected)'
                      : (report.details || 'No provided comment')
                  }</p>
                </div>

                {report.post_id && (
                  <div className="report-target">
                    <strong>Reported Post:</strong>
                    <div className="reported-post-content">
                      {report.post ? (
                        <p className="post-preview">
                          {report.post.content.length > 200 
                            ? report.post.content.substring(0, 200) + '...' 
                            : report.post.content
                          }
                        </p>
                      ) : (
                        <span>Post ID: {report.post_id}</span>
                      )}
                    </div>
                  </div>
                )}

                {report.reported_user_id && (
                  <div className="report-target">
                    <strong>Reported User:</strong>
                    <span>
                      {report.reported_user 
                        ? `${report.reported_user.display_name} (ID: ${report.reported_user_id})`
                        : `User ID: ${report.reported_user_id}`
                      }
                    </span>
                  </div>
                )}

                {report.status === 'open' && (
                  <div className="report-actions">
                    {report.is_crisis ? (
                      /* Crisis reports: Delete Post and Dismiss only */
                      <>
                        <button
                          className="btn-danger"
                          onClick={() => openActionDialog(report.id, 'delete_post')}
                          disabled={!report.post_id}
                          title={!report.post_id ? 'No post associated with this crisis' : 'Delete the crisis post'}
                        >
                          Delete Post
                        </button>
                        <button
                          className="btn-secondary"
                          onClick={() => openActionDialog(report.id, 'dismiss')}
                        >
                          Dismiss
                        </button>
                      </>
                    ) : (
                      /* Regular reports: Delete Post (warns user), Delete Account (bans & deletes), Dismiss */
                      <>
                        <button
                          className="btn-warn"
                          onClick={() => openActionDialog(report.id, 'delete_post')}
                          disabled={!report.post_id}
                          title={!report.post_id ? 'No post associated with this report' : 'Delete post and warn user'}
                        >
                          Delete Post
                        </button>
                        <button
                          className="btn-danger"
                          onClick={() => openActionDialog(report.id, 'delete_account')}
                          disabled={!report.reported_user_id}
                          title={!report.reported_user_id ? 'No user associated with this report' : 'Ban and delete user account'}
                        >
                          Delete Account
                        </button>
                        <button
                          className="btn-secondary"
                          onClick={() => openActionDialog(report.id, 'dismiss')}
                        >
                          Dismiss
                        </button>
                      </>
                    )}
                    {selectedReport === report.id && (
                      <div className="action-reason-input">
                        <textarea
                          placeholder={`Enter reason for ${selectedAction === 'delete_post' ? 'deleting post' : selectedAction === 'delete_account' ? 'deleting account' : selectedAction} action`}
                          value={actionReason}
                          onChange={(e) => setActionReason(e.target.value)}
                          rows="3"
                        />
                        <div className="action-buttons">
                          <button
                            className="btn-primary"
                            onClick={() => handleDetermineAction(report.id, selectedAction)}
                          >
                            Confirm {selectedAction === 'delete_post' ? 'Delete Post' : selectedAction === 'delete_account' ? 'Delete Account' : selectedAction}
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
    </div>
  )
}

export default Moderation

