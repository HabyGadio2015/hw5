import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from './api'
import ApprovalPanel from './components/ApprovalPanel'
import AgentStage from './components/AgentStage'
import Header from './components/Header'
import ResolutionPanel from './components/ResolutionPanel'
import TicketBoard from './components/TicketBoard'
import type { AgentEvent, AgentReply, CashBalance, PaymentProposal, TicketSummary } from './types'

const POLL_MS = 1200

export default function App() {
  const [tickets, setTickets] = useState<TicketSummary[]>([])
  const [cash, setCash] = useState<CashBalance | null>(null)
  const [selectedId, setSelectedId] = useState<number | null>(null)
  const [running, setRunning] = useState(false)
  const [events, setEvents] = useState<AgentEvent[]>([])
  const [outcomes, setOutcomes] = useState<Record<number, AgentReply | undefined>>({})
  const [pendingProposal, setPendingProposal] = useState<{
    ticketId: number
    proposal: PaymentProposal
  } | null>(null)
  const [approving, setApproving] = useState(false)
  const [resetting, setResetting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const runStartRef = useRef<string | null>(null)
  const pollRef = useRef<number | null>(null)

  const refreshTickets = useCallback(async () => {
    try {
      setTickets(await api.getTickets())
    } catch (e) {
      setError(String(e))
    }
  }, [])

  const refreshCash = useCallback(async () => {
    try {
      setCash(await api.getCash())
    } catch (e) {
      setError(String(e))
    }
  }, [])

  useEffect(() => {
    refreshTickets()
    refreshCash()
  }, [refreshTickets, refreshCash])

  useEffect(() => {
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current)
    }
  }, [])

  const pollEvents = useCallback(async () => {
    try {
      const all = await api.getEvents(50)
      const since = runStartRef.current
      // Compare as real instants, not raw strings: the backend's audit
      // timestamps use Python's "+00:00" suffix with 1-second resolution
      // (no fractional seconds), which does not sort correctly against
      // JS's "Z"-suffixed, millisecond-precision ISO strings.
      const sinceMs = since ? new Date(since).getTime() : null
      const filtered = sinceMs === null ? all : all.filter((e) => new Date(e.time).getTime() >= sinceMs)
      setEvents([...filtered].reverse())
    } catch (e) {
      console.error(e)
    }
  }, [])

  const activeAgent = events.length > 0 ? events[events.length - 1].agent : null

  async function handleStart() {
    if (selectedId === null || running) return
    const ticketId = selectedId
    setError(null)
    setEvents([])
    setOutcomes((prev) => ({ ...prev, [ticketId]: undefined }))
    setPendingProposal(null)
    // Back the run-start marker up by a couple seconds: the backend's audit
    // timestamps only have 1-second resolution, so an event in the same
    // wall-clock second as this click could otherwise be missed.
    runStartRef.current = new Date(Date.now() - 2000).toISOString()
    setRunning(true)
    pollRef.current = window.setInterval(pollEvents, POLL_MS)
    pollEvents()

    try {
      const reply = await api.runTicket(ticketId)
      setOutcomes((prev) => ({ ...prev, [ticketId]: reply }))
      if (reply.needs_human_approval && reply.payment_proposal) {
        setPendingProposal({ ticketId, proposal: reply.payment_proposal })
      }
    } catch (e) {
      setError(String(e))
    } finally {
      if (pollRef.current) window.clearInterval(pollRef.current)
      pollRef.current = null
      await pollEvents()
      setRunning(false)
      await refreshTickets()
      await refreshCash()
    }
  }

  async function handleApprove(approvedBy: string) {
    if (!pendingProposal) return
    setApproving(true)
    try {
      const result = await api.approvePayment({
        kind: pendingProposal.proposal.kind,
        ref_id: pendingProposal.proposal.ref_id,
        amount: pendingProposal.proposal.amount,
        account: pendingProposal.proposal.account,
        approved_by: approvedBy,
      })
      if (!result.success) {
        setError(result.reason ?? 'Payment refused')
      } else {
        await refreshCash()
      }
      setPendingProposal(null)
    } catch (e) {
      setError(String(e))
    } finally {
      setApproving(false)
    }
  }

  async function handleReset() {
    if (!window.confirm("Reset the desk to the original seed data? This clears today's progress.")) {
      return
    }
    setResetting(true)
    try {
      await api.reset()
      setSelectedId(null)
      setEvents([])
      setOutcomes({})
      setPendingProposal(null)
      await refreshTickets()
      await refreshCash()
    } catch (e) {
      setError(String(e))
    } finally {
      setResetting(false)
    }
  }

  const selectedTicket = tickets.find((t) => t.id === selectedId)
  const currentOutcome = selectedId !== null ? outcomes[selectedId] : undefined

  return (
    <div className="app">
      <Header balance={cash?.balance ?? null} onReset={handleReset} resetting={resetting} />

      {error && (
        <div className="error-banner" onClick={() => setError(null)}>
          {error} <span className="error-dismiss">(dismiss)</span>
        </div>
      )}

      <main className="board">
        <TicketBoard
          tickets={tickets}
          selectedId={selectedId}
          onSelect={setSelectedId}
          running={running}
          outcomes={outcomes}
        />

        <section className="stage-panel">
          <div className="run-controls">
            <button
              className="btn btn-primary"
              disabled={selectedId === null || running}
              onClick={handleStart}
            >
              {running
                ? 'Agents working…'
                : selectedId === null
                  ? 'Pick a ticket first'
                  : `Start the Team on #${selectedId}`}
            </button>
          </div>

          <AgentStage events={events} running={running} activeAgent={activeAgent} />

          {currentOutcome && !running && (
            <ResolutionPanel reply={currentOutcome} ticket={selectedTicket} events={events} />
          )}

          {pendingProposal && (
            <ApprovalPanel
              proposal={pendingProposal.proposal}
              onApprove={handleApprove}
              onDecline={() => setPendingProposal(null)}
              busy={approving}
            />
          )}
        </section>
      </main>
    </div>
  )
}
