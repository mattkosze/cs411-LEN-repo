import { useState } from 'react'
import './ReportModal.css'

const REPORT_REASONS = [
  { value: 'harassment', label: 'Harassment', description: 'Bullying, threats, or targeted attacks' },
  { value: 'spam', label: 'Spam', description: 'Unwanted promotional content or repetitive posts' },
  { value: 'inappropriate', label: 'Inappropriate Content', description: 'Content that violates community guidelines' },
  { value: 'crisis', label: 'Crisis', description: 'User may be in danger or need immediate support' },
]

function ReportModal({ post, onClose, onSubmit, isSubmitting }) {
  const [selectedReason, setSelectedReason] = useState('')
  const [details, setDetails] = useState('')
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    if (!selectedReason) {
      setError('Please select a reason for your report')
      return
    }

    try {
      await onSubmit({
        reason: selectedReason,
        details: details.trim() || null,
      })
    } catch (err) {
      setError(err.message || 'Failed to submit report')
    }
  }

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose()
    }
  }

  const selectedReasonData = REPORT_REASONS.find(r => r.value === selectedReason)

  return (
    <div className="report-modal-backdrop" onClick={handleBackdropClick}>
      <div className="report-modal">
        <div className="report-modal-header">
          <h2>Report Post</h2>
          <button className="close-button" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>

        <div className="report-modal-content">
          <p className="report-intro">
            Help us keep the community safe. Select a reason for reporting this post.
          </p>

          {error && (
            <div className="report-error">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="reason-options">
              {REPORT_REASONS.map((reason) => (
                <label
                  key={reason.value}
                  className={`reason-option ${selectedReason === reason.value ? 'selected' : ''} ${reason.value === 'crisis' ? 'crisis-option' : ''}`}
                >
                  <input
                    type="radio"
                    name="reason"
                    value={reason.value}
                    checked={selectedReason === reason.value}
                    onChange={(e) => setSelectedReason(e.target.value)}
                  />
                  <div className="reason-content">
                    <span className="reason-label">{reason.label}</span>
                    <span className="reason-description">{reason.description}</span>
                  </div>
                </label>
              ))}
            </div>

            {selectedReason === 'crisis' && (
              <div className="crisis-notice">
                <strong>⚠️ Crisis Report</strong>
                <p>
                  This will immediately alert our moderation team. If you believe this person
                  is in immediate danger, please also contact emergency services.
                </p>
              </div>
            )}

            <div className="details-section">
              <label htmlFor="report-details">Additional details (optional)</label>
              <textarea
                id="report-details"
                value={details}
                onChange={(e) => setDetails(e.target.value)}
                placeholder="Provide any additional context that may help our moderators..."
                rows={3}
                maxLength={500}
              />
              <span className="char-count">{details.length}/500</span>
            </div>

            <div className="report-modal-actions">
              <button
                type="button"
                className="btn-cancel"
                onClick={onClose}
                disabled={isSubmitting}
              >
                Cancel
              </button>
              <button
                type="submit"
                className={`btn-submit ${selectedReason === 'crisis' ? 'btn-crisis' : ''}`}
                disabled={isSubmitting || !selectedReason}
              >
                {isSubmitting ? 'Submitting...' : 'Submit Report'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

export default ReportModal

