import { useState, type CSSProperties } from 'react'
import { AGENT_META, AGENT_ORDER } from '../agentMeta'
import type { AgentEvent, AgentRole } from '../types'

interface Props {
  events: AgentEvent[]
  running: boolean
  activeAgent: string | null
}

export default function AgentStage({ events, running, activeAgent }: Props) {
  const [filter, setFilter] = useState<AgentRole | null>(null)
  const shown = filter ? events.filter((e) => e.agent === filter) : events

  return (
    <section className="agent-stage">
      <h2 className="panel-title">The Team</h2>
      <p className="panel-sub">Click an agent to see only its messages.</p>
      <div className="avatar-row">
        {AGENT_ORDER.map((role) => {
          const meta = AGENT_META[role]
          const isActive = running && activeAgent === role
          const hasSpoken = events.some((e) => e.agent === role)
          const isFiltered = filter === role
          return (
            <button
              type="button"
              key={role}
              className={`avatar ${isActive ? 'avatar--active' : ''} ${hasSpoken ? 'avatar--spoken' : ''} ${isFiltered ? 'avatar--filtered' : ''}`}
              style={
                {
                  '--agent-color': meta.color,
                  '--agent-glow': meta.glow,
                } as CSSProperties
              }
              title={meta.blurb}
              aria-pressed={isFiltered}
              onClick={() => setFilter(isFiltered ? null : role)}
            >
              <div className="avatar-glyph">{meta.glyph}</div>
              <div className="avatar-label">{meta.label}</div>
              {isActive && <div className="avatar-pulse" />}
            </button>
          )
        })}
      </div>

      {filter && (
        <div className="feed-filter">
          Showing only <strong>{AGENT_META[filter].label}</strong>
          <button type="button" className="feed-filter-clear" onClick={() => setFilter(null)}>
            Show all
          </button>
        </div>
      )}

      <div className="event-feed">
        {events.length === 0 && !running && (
          <div className="event-feed-empty">
            Pick a ticket and start the team to watch them work.
          </div>
        )}
        {running && events.length === 0 && (
          <div className="event-feed-empty event-feed-empty--loading">
            <span className="dot-flashing" /> BOSS is reading the ticket…
          </div>
        )}
        {filter && events.length > 0 && shown.length === 0 && (
          <div className="event-feed-empty">
            {AGENT_META[filter].label} hasn't said anything on this ticket.
          </div>
        )}
        {shown.map((e, i) => {
          const meta = AGENT_META[e.agent] ?? AGENT_META.boss
          return (
            <div
              key={`${e.time}-${i}`}
              className="event-bubble"
              style={{ '--agent-color': meta.color } as CSSProperties}
            >
              <div className="event-bubble-avatar">{meta.glyph}</div>
              <div className="event-bubble-body">
                <div className="event-bubble-head">
                  <span className="event-bubble-agent">{meta.label}</span>
                  {e.delegation_trail.length > 0 && (
                    <span className="event-bubble-trail">
                      {e.delegation_trail[e.delegation_trail.length - 1]}
                    </span>
                  )}
                </div>
                <div className="event-bubble-said">{e.said || '…thinking'}</div>
                {e.tools_used.length > 0 && (
                  <div className="event-bubble-tools">
                    {e.tools_used.map((tool) => (
                      <span key={tool} className="tool-chip">
                        {tool}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
