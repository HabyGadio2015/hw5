import { useState } from 'react'
import type { PaymentProposal } from '../types'

interface Props {
  proposal: PaymentProposal
  onApprove: (approvedBy: string) => void
  onDecline: () => void
  busy: boolean
}

export default function ApprovalPanel({ proposal, onApprove, onDecline, busy }: Props) {
  const [name, setName] = useState('')

  return (
    <div className="approval-panel">
      <div className="approval-head">
        <span className="approval-icon">✋</span>
        <span>Human approval required</span>
      </div>
      <p className="approval-reason">
        {proposal.reason ?? `ACCOUNTING recommends paying ${proposal.kind} #${proposal.ref_id}.`}
      </p>
      <div className="approval-amount">
        ${proposal.amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
        <span className="approval-amount-sub">
          {' '}
          from {proposal.account} · {proposal.kind} #{proposal.ref_id}
        </span>
      </div>
      <div className="approval-form">
        <input
          type="text"
          placeholder="Type your name to approve"
          value={name}
          onChange={(e) => setName(e.target.value)}
          disabled={busy}
        />
        <div className="approval-buttons">
          <button
            className="btn btn-approve"
            disabled={busy || !name.trim()}
            onClick={() => onApprove(name.trim())}
          >
            {busy ? 'Approving…' : 'Approve Payment'}
          </button>
          <button className="btn btn-ghost" disabled={busy} onClick={onDecline}>
            Decline
          </button>
        </div>
      </div>
    </div>
  )
}
