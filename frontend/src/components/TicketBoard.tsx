import type { AgentReply, TicketSummary } from '../types'

interface Props {
  tickets: TicketSummary[]
  selectedId: number | null
  onSelect: (id: number) => void
  running: boolean
  outcomes: Record<number, AgentReply | undefined>
}

const TYPE_LABEL: Record<string, string> = {
  customer_order: 'Customer Order',
  rent_notice: 'Rent Notice',
  price_override: 'Price Override',
}

export default function TicketBoard({ tickets, selectedId, onSelect, running, outcomes }: Props) {
  return (
    <section className="ticket-board">
      <h2 className="panel-title">The Board</h2>
      <p className="panel-sub">Pick one ticket, then start the team on it.</p>
      <div className="ticket-list">
        {tickets.map((t) => {
          const outcome = outcomes[t.id]
          const isSelected = t.id === selectedId
          let badge: { text: string; cls: string } | null = null
          if (outcome) {
            if (outcome.needs_human_approval) badge = { text: 'Needs Approval', cls: 'badge-approval' }
            else if (outcome.resolved) badge = { text: 'Resolved', cls: 'badge-resolved' }
            else badge = { text: 'Not Resolved', cls: 'badge-partial' }
          }
          return (
            <button
              key={t.id}
              className={`ticket-card ${isSelected ? 'ticket-card--selected' : ''}`}
              onClick={() => onSelect(t.id)}
              disabled={running}
            >
              <div className="ticket-card-top">
                <span className="ticket-id">#{t.id}</span>
                <span className="ticket-type">{TYPE_LABEL[t.type] ?? t.type}</span>
              </div>
              <div className="ticket-subject">{t.subject}</div>
              <div className="ticket-requester">{t.requester}</div>
              <div className="ticket-card-bottom">
                <span className={`status-pill ${t.is_open ? 'status-open' : 'status-closed'}`}>
                  {t.status}
                </span>
                {badge && <span className={`outcome-badge ${badge.cls}`}>{badge.text}</span>}
              </div>
            </button>
          )
        })}
      </div>
    </section>
  )
}
