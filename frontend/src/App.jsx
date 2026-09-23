import { useEffect, useState } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function App() {
  const [page, setPage] = useState('dashboard')
  const [transactions, setTransactions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const [selectedPayment, setSelectedPayment] = useState(null)
  const [investigation, setInvestigation] = useState(null)
  const [investigationLoading, setInvestigationLoading] = useState(false)
  const [investigationError, setInvestigationError] = useState('')

  const [actionReviewOpen, setActionReviewOpen] = useState(false)
  const [actionApproving, setActionApproving] = useState(false)
  const [actionApproved, setActionApproved] = useState(false)
  const [actionApprovalError, setActionApprovalError] = useState('')
  const [approvalRecorded, setApprovalRecorded] = useState(false)

  const fetchReconciliation = async () => {
    try {
      setLoading(true)
      setError('')

      const response = await fetch(`${API_URL}/reconciliation`)

      if (!response.ok) {
        throw new Error('Failed to fetch reconciliation data')
      }

      const data = await response.json()
      setTransactions(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const openInvestigation = async (paymentId) => {
    setSelectedPayment(paymentId)
    setInvestigation(null)
    setInvestigationError('')
    setActionReviewOpen(false)
    setActionApproved(false)
    setApprovalRecorded(false)
    setActionApprovalError('')
    setInvestigationLoading(true)

    try {
      const response = await fetch(
        `${API_URL}/investigations/${paymentId}`
      )

      if (!response.ok) {
        throw new Error('Failed to load investigation')
      }

      const data = await response.json()
      setInvestigation(data)

      try {
        const auditResponse = await fetch(
          `${API_URL}/investigations/${paymentId}/audit`
        )

        if (auditResponse.ok) {
          const auditEvents = await auditResponse.json()

          const hasApproval = auditEvents.some(
            (event) => event.event_type === 'action_approved'
          )

          setApprovalRecorded(hasApproval)
        }
      } catch {
        // Audit lookup should not prevent investigation from loading.
      }
    } catch (err) {
      setInvestigationError(err.message)
    } finally {
      setInvestigationLoading(false)
    }
  }

  const closeInvestigation = () => {
    setActionReviewOpen(false)
    setSelectedPayment(null)
    setInvestigation(null)
    setInvestigationError('')
    setActionApprovalError('')
  }

  const openActionReview = () => {
    setActionReviewOpen(true)
    setActionApprovalError('')
  }

  const approveAction = async () => {
    if (!selectedPayment) return

    setActionApproving(true)
    setActionApprovalError('')

    try {
      const response = await fetch(
        `${API_URL}/investigations/${selectedPayment}/approve`,
        {
          method: 'POST',
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || 'Failed to approve action'
        )
      }

      setActionApproved(true)
      setApprovalRecorded(true)
    } catch (err) {
      setActionApprovalError(err.message)
    } finally {
      setActionApproving(false)
    }
  }

  useEffect(() => {
    fetchReconciliation()
  }, [])

  const totalTransactions = transactions.length

  const exceptions = transactions.filter(
    (item) => item.status === 'exception'
  ).length

  const matched = transactions.filter(
    (item) => item.status === 'matched'
  ).length

  const critical = transactions.filter(
    (item) =>
      item.exception_type === 'bank_mismatch' ||
      item.exception_type === 'duplicate_settlement'
  ).length

  const formatAmount = (amount) => {
    if (amount === null || amount === undefined) {
      return '—'
    }

    return `₹${amount.toLocaleString('en-IN', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`
  }

  const formatException = (exception) => {
    if (!exception) return '—'

    return exception
      .replaceAll('_', ' ')
      .replace(/\b\w/g, (letter) => letter.toUpperCase())
  }

  const formatRecommendation = (value) => {
    if (!value) return '—'

    return value
      .replaceAll('_', ' ')
      .replace(/\b\w/g, (letter) => letter.toUpperCase())
  }

  const Dashboard = () => (
    <>
      <header className="header">
        <div>
          <h1>Reconciliation Overview</h1>
          <p>Monitor transactions and investigate exceptions.</p>
        </div>

        <button
          className="refresh-btn"
          onClick={fetchReconciliation}
        >
          ↻ Refresh
        </button>
      </header>

      <section className="metrics">
        <div className="metric-card">
          <span>Transactions</span>
          <strong>{loading ? '—' : totalTransactions}</strong>
          <small>Total processed</small>
        </div>

        <div className="metric-card">
          <span>Exceptions</span>
          <strong>{loading ? '—' : exceptions}</strong>
          <small>Require attention</small>
        </div>

        <div className="metric-card">
          <span>Matched</span>
          <strong>{loading ? '—' : matched}</strong>
          <small>Successfully reconciled</small>
        </div>

        <div className="metric-card critical">
          <span>Critical</span>
          <strong>{loading ? '—' : critical}</strong>
          <small>High priority</small>
        </div>
      </section>

      <ReconciliationTable />
    </>
  )

  const ReconciliationTable = () => (
    <section className="content-card">
      <div className="section-header">
        <div>
          <h2>Reconciliation Results</h2>
          <p>Payment-level reconciliation status</p>
        </div>

        <span className="live-badge">● LIVE</span>
      </div>

      {loading && (
        <div className="message">
          Loading reconciliation data...
        </div>
      )}

      {error && (
        <div className="message error-message">
          {error}
        </div>
      )}

      {!loading && !error && (
        <table>
          <thead>
            <tr>
              <th>Payment</th>
              <th>Status</th>
              <th>Expected</th>
              <th>Settled</th>
              <th>Difference</th>
              <th>Exception</th>
            </tr>
          </thead>

          <tbody>
            {transactions.map((transaction) => (
              <tr
                key={transaction.payment_id}
                className={
                  selectedPayment === transaction.payment_id
                    ? 'selected-row'
                    : ''
                }
                onClick={() =>
                  transaction.status === 'exception' &&
                  openInvestigation(transaction.payment_id)
                }
                style={{
                  cursor:
                    transaction.status === 'exception'
                      ? 'pointer'
                      : 'default',
                }}
              >
                <td>{transaction.payment_id}</td>

                <td>
                  <span
                    className={`badge ${
                      transaction.status === 'matched'
                        ? 'matched'
                        : 'exception'
                    }`}
                  >
                    {transaction.status === 'matched'
                      ? 'Matched'
                      : 'Exception'}
                  </span>
                </td>

                <td>
                  {formatAmount(transaction.expected_amount)}
                </td>

                <td>
                  {formatAmount(transaction.settled_amount)}
                </td>

                <td>
                  {formatAmount(transaction.difference)}
                </td>

                <td>
                  {formatException(transaction.exception_type)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )

  const Investigations = () => {
    const exceptionTransactions = transactions.filter(
      (item) => item.status === 'exception'
    )

    return (
      <>
        <header className="header">
          <div>
            <h1>Investigations</h1>
            <p>
              AI-powered analysis of reconciliation exceptions.
            </p>
          </div>
        </header>

        <section className="content-card">
          <div className="section-header">
            <div>
              <h2>Open Exceptions</h2>
              <p>
                Select an exception to launch an investigation.
              </p>
            </div>

            <span className="live-badge">
              {exceptionTransactions.length} OPEN
            </span>
          </div>

          <div className="investigation-list">
            {exceptionTransactions.map((transaction) => (
              <div
                className="investigation-row"
                key={transaction.payment_id}
                onClick={() =>
                  openInvestigation(transaction.payment_id)
                }
              >
                <div>
                  <strong>{transaction.payment_id}</strong>

                  <span>
                    {formatException(
                      transaction.exception_type
                    )}
                  </span>
                </div>

                <div className="investigation-difference">
                  {formatAmount(transaction.difference)}
                </div>

                <button>
                  Investigate →
                </button>
              </div>
            ))}
          </div>
        </section>
      </>
    )
  }

  const AuditTrail = () => {
    const [auditEvents, setAuditEvents] = useState([])
    const [auditLoading, setAuditLoading] = useState(true)

    useEffect(() => {
      const loadAudit = async () => {
        try {
          const results = await Promise.all(
            transactions
              .filter((item) => item.status === 'exception')
              .map(async (item) => {
                const response = await fetch(
                  `${API_URL}/investigations/${item.payment_id}/audit`
                )

                if (!response.ok) return []

                return response.json()
              })
          )

          const events = results
            .flat()
            .sort(
              (a, b) =>
                new Date(b.created_at) -
                new Date(a.created_at)
            )

          setAuditEvents(events)
        } catch {
          setAuditEvents([])
        } finally {
          setAuditLoading(false)
        }
      }

      if (transactions.length > 0) {
        loadAudit()
      } else {
        setAuditLoading(false)
      }
    }, [])

    const getEventType = (event) => {
      if (event.event_type === 'action_approved') {
        return 'Human Approval'
      }

      if (event.event_type === 'investigation_completed') {
        return 'AI Investigation'
      }

      return formatException(event.event_type)
    }

    const getEventIcon = (event) => {
      if (event.event_type === 'action_approved') {
        return '✓'
      }

      if (event.event_type === 'investigation_completed') {
        return 'AI'
      }

      return '•'
    }

    return (
      <>
        <header className="header">
          <div>
            <h1>Audit Trail</h1>
            <p>
              Investigation activity and human decisions.
            </p>
          </div>
        </header>

        <section className="content-card audit-card">
          <div className="section-header">
            <div>
              <h2>Decision History</h2>
              <p>
                A traceable record of investigation and approval
                activity.
              </p>
            </div>

            <span className="live-badge">
              {auditEvents.length} EVENTS
            </span>
          </div>

          {auditLoading ? (
            <div className="message">
              Loading audit events...
            </div>
          ) : auditEvents.length === 0 ? (
            <div className="message">
              No audit events available yet.
            </div>
          ) : (
            <div className="audit-timeline">
              {auditEvents.map((event, index) => {
                const isApproval =
                  event.event_type === 'action_approved'

                return (
                  <div
                    className={`audit-event ${
                      isApproval
                        ? 'audit-event-approval'
                        : 'audit-event-ai'
                    }`}
                    key={`${event.payment_id}-${event.created_at}-${index}`}
                  >
                    <div className="audit-event-marker">
                      {getEventIcon(event)}
                    </div>

                    <div className="audit-event-content">
                      <div className="audit-event-top">
                        <div>
                          <span className="audit-event-type">
                            {getEventType(event)}
                          </span>

                          <strong>
                            {event.payment_id}
                          </strong>
                        </div>

                        <time>
                          {new Date(
                            event.created_at
                          ).toLocaleString()}
                        </time>
                      </div>

                      <p className="audit-event-description">
                        {event.description}
                      </p>

                      <div className="audit-event-meta">
                        <span>Actor</span>

                        <strong>
                          {event.actor}
                        </strong>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </section>
      </>
    )
  }

  const renderPage = () => {
    if (page === 'reconciliation') {
      return <ReconciliationTable />
    }

    if (page === 'investigations') {
      return <Investigations />
    }

    if (page === 'audit') {
      return <AuditTrail />
    }

    return <Dashboard />
  }

  return (
    <div className="app">

      {/* SIDEBAR */}

      <aside className="sidebar">
        <div className="logo">
          <div className="logo-mark">R</div>

          <div>
            <h2>ReconSense</h2>
            <span>Financial Intelligence</span>
          </div>
        </div>

        <nav>
          <div
            className={`nav-item ${
              page === 'dashboard' ? 'active' : ''
            }`}
            onClick={() => setPage('dashboard')}
          >
            Dashboard
          </div>

          <div
            className={`nav-item ${
              page === 'reconciliation' ? 'active' : ''
            }`}
            onClick={() => setPage('reconciliation')}
          >
            Reconciliation
          </div>

          <div
            className={`nav-item ${
              page === 'investigations' ? 'active' : ''
            }`}
            onClick={() => setPage('investigations')}
          >
            Investigations
          </div>

          <div
            className={`nav-item ${
              page === 'audit' ? 'active' : ''
            }`}
            onClick={() => setPage('audit')}
          >
            Audit Trail
          </div>
        </nav>

        <div className="system-status">
          <span className="status-dot"></span>
          System Operational
        </div>
      </aside>

      {/* MAIN */}

      <main className="main">
        {renderPage()}
      </main>

      {/* INVESTIGATION PANEL */}

      {selectedPayment && (
        <div className="investigation-overlay">
          <div className="investigation-panel">

            <div className="investigation-header">
              <div>
                <span className="panel-label">
                  AI INVESTIGATION
                </span>

                <h2>{selectedPayment}</h2>

                <p>
                  Exception analysis and recommended action
                </p>
              </div>

              <button
                className="close-btn"
                onClick={closeInvestigation}
              >
                ×
              </button>
            </div>

            {investigationLoading && (
              <div className="investigation-loading">
                <div className="loading-icon">◌</div>

                <h3>
                  Investigating exception...
                </h3>

                <p>
                  ReconSense is analyzing reconciliation
                  evidence.
                </p>
              </div>
            )}

            {investigationError && (
              <div className="investigation-error">
                {investigationError}
              </div>
            )}

            {investigation && (
              <div className="investigation-content">

                <div className="investigation-status">
                  <div>
                    <span className="panel-label">
                      EXCEPTION
                    </span>

                    <h3>
                      {formatException(
                        investigation.exception_type
                      )}
                    </h3>
                  </div>

                  <div className="confidence">
                    <span>Confidence</span>

                    <strong>
                      {Math.round(
                        investigation.confidence * 100
                      )}
                      %
                    </strong>
                  </div>
                </div>

                <div className="financial-summary">

                  <div className="financial-item">
                    <span>Expected Payment</span>

                    <strong>
                      {formatAmount(
                        investigation.expected_amount
                      )}
                    </strong>
                  </div>

                  <div className="financial-item">
                    <span>Settlement</span>

                    <strong>
                      {formatAmount(
                        investigation.settled_amount
                      )}
                    </strong>
                  </div>

                  <div className="financial-item">
                    <span>Bank Credit</span>

                    <strong>
                      {formatAmount(
                        investigation.bank_amount
                      )}
                    </strong>
                  </div>

                  <div className="financial-item discrepancy">
                    <span>Discrepancy</span>

                    <strong>
                      {formatAmount(
                        investigation.difference
                      )}
                    </strong>
                  </div>

                </div>

                <div className="investigation-section">
                  <span className="panel-label">
                    LIKELY CAUSE
                  </span>

                  <p className="cause">
                    {investigation.likely_cause}
                  </p>
                </div>

                <div className="investigation-section">
                  <span className="panel-label">
                    ANALYSIS
                  </span>

                  <p>
                    {investigation.explanation}
                  </p>
                </div>

                <div className="investigation-section">
                  <span className="panel-label">
                    EVIDENCE
                  </span>

                  <div className="evidence-list">
                    {investigation.evidence_references.map(
                      (reference) => (
                        <div
                          className="evidence-item"
                          key={reference}
                        >
                          <span className="evidence-icon">
                            ↗
                          </span>

                          {reference}
                        </div>
                      )
                    )}
                  </div>
                </div>

                <div
                  className={`recommendation-box ${
                    approvalRecorded
                      ? 'recommendation-approved'
                      : ''
                  }`}
                  onClick={openActionReview}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (
                      e.key === 'Enter' ||
                      e.key === ' '
                    ) {
                      e.preventDefault()
                      openActionReview()
                    }
                  }}
                >
                  <div>
                    <span className="panel-label">
                      {approvalRecorded
                        ? 'ACTION STATUS'
                        : 'RECOMMENDED ACTION'}
                    </span>

                    <h3>
                      {approvalRecorded
                        ? '✓ Approved & Recorded'
                        : formatRecommendation(
                            investigation.recommendation
                          )}
                    </h3>
                  </div>

                  <span className="action-arrow">
                    →
                  </span>
                </div>

                <div
                  className={`governance-box ${
                    approvalRecorded
                      ? 'governance-approved'
                      : ''
                  }`}
                >
                  <div className="governance-icon">
                    ✓
                  </div>

                  <div>
                    <span className="panel-label">
                      GOVERNANCE
                    </span>

                    <strong>
                      {approvalRecorded
                        ? 'Action Approved'
                        : formatRecommendation(
                            investigation.governance_decision
                          )}
                    </strong>

                    <p>
                      {approvalRecorded
                        ? 'Human approval recorded. The decision has been added to the audit trail.'
                        : investigation.governance_reason}
                    </p>
                  </div>
                </div>

              </div>
            )}

          </div>

          {/* ACTION REVIEW */}

          {actionReviewOpen && (
            <div
              className="action-review-overlay"
              onClick={() => setActionReviewOpen(false)}
            >
              <div
                className="action-review-modal"
                onClick={(e) => e.stopPropagation()}
              >

                <div className="action-review-header">
                  <div>
                    <span className="panel-label">
                      ACTION REVIEW
                    </span>

                    <h2>
                      {investigation
                        ? formatRecommendation(
                            investigation.recommendation
                          )
                        : 'Review Action'}
                    </h2>
                  </div>

                  <button
                    className="close-btn"
                    onClick={() =>
                      setActionReviewOpen(false)
                    }
                  >
                    ×
                  </button>
                </div>

                <div className="action-review-content">

                  <div className="review-status">
                    <span>
                      Governance Status
                    </span>

                    <strong>
                      {investigation
                        ? formatRecommendation(
                            investigation.governance_decision
                          )
                        : 'Approval Required'}
                    </strong>
                  </div>

                  <p>
                    ReconSense recommends this action based
                    on the reconciliation exception, available
                    evidence, and investigation analysis.
                  </p>

                  <div className="review-summary">

                    <div>
                      <span>Payment</span>

                      <strong>
                        {selectedPayment || '—'}
                      </strong>
                    </div>

                    <div>
                      <span>Discrepancy</span>

                      <strong>
                        {investigation
                          ? formatAmount(
                              investigation.difference
                            )
                          : '—'}
                      </strong>
                    </div>

                  </div>

                  <div className="review-warning">
                    <strong>
                      Human approval required
                    </strong>

                    <p>
                      This action should be reviewed by an
                      authorized operator before any financial
                      record is changed.
                    </p>
                  </div>

                  {actionApprovalError && (
                    <div className="review-approval-error">
                      {actionApprovalError}
                    </div>
                  )}

                  <div className="review-actions">

                    <button
                      className="secondary-action"
                      onClick={() =>
                        setActionReviewOpen(false)
                      }
                    >
                      Cancel
                    </button>

                    <button
                      className="primary-action"
                      onClick={approveAction}
                      disabled={
                        actionApproving ||
                        actionApproved ||
                        approvalRecorded
                      }
                    >
                      {actionApproving
                        ? 'Recording...'
                        : actionApproved ||
                            approvalRecorded
                          ? '✓ Approved & Recorded'
                          : 'Approve Review'}
                    </button>

                  </div>

                </div>

              </div>
            </div>
          )}

        </div>
      )}
    </div>
  )
}

export default App