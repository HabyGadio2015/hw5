import { AGENT_META, AGENT_ORDER } from '../agentMeta'
import type { AgentEvent, AgentReply, TicketSummary } from '../types'

interface Props {
  reply: AgentReply
  ticket: TicketSummary | undefined
  events: AgentEvent[]
}

export default function ResolutionPanel({ reply, ticket, events }: Props) {
  const mismatch = reply.resolved && ticket?.is_open === true

  // Latest thing each agent said in this run, plus every tool it used.
  const perAgent = AGENT_ORDER.flatMap((role) => {
    const mine = events.filter((e) => e.agent === role)
    if (mine.length === 0) return []
    const tools = [...new Set(mine.flatMap((e) => e.tools_used))]
    return [{ role, said: mine[mine.length - 1].said, tools }]
  })

  return (
    <div className={`resolution-panel ${reply.resolved ? 'resolution-panel--ok' : 'resolution-panel--partial'}`}>
      <div className="resolution-head">
        <span className="resolution-icon">{reply.resolved ? '✓' : '⚑'}</span>
        <span className="resolution-verdict">{reply.resolved ? 'Resolved' : 'Not Resolved'}</span>
      </div>
      <p className="resolution-summary">{reply.summary}</p>
      {!reply.resolved && reply.partial_fulfillment_note && (
        <p className="resolution-note">
          <strong>Partial Fulfillment:</strong> {reply.partial_fulfillment_note}
        </p>
      )}
      {perAgent.length > 0 && (
        <div className="resolution-agents">
          <strong>What each agent did</strong>
          <ul>
            {perAgent.map((a) => (
              <li key={a.role}>
                <span className="resolution-agent-name">{AGENT_META[a.role].label}:</span> {a.said}
                {a.tools.length > 0 && <span className="resolution-agent-tools"> ({a.tools.join(', ')})</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
      {mismatch && (
        <p className="resolution-mismatch">
          ⚠ BOSS reported this resolved, but the ticket is still <code>{ticket?.status}</code> on the
          board — no one marked it resolved with <code>update_ticket_status</code>. Flagging it rather
          than trusting the claim.
        </p>
      )}
    </div>
  )
}
