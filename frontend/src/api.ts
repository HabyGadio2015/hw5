import type {
  AgentEvent,
  AgentReply,
  ApprovePaymentResult,
  CashBalance,
  ResetResult,
  TicketSummary,
} from './types'

const BASE_URL = 'http://localhost:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(`${init?.method ?? 'GET'} ${path} -> ${res.status}: ${body}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  getTickets: () => request<TicketSummary[]>('/tickets'),

  runTicket: (ticketId: number) =>
    request<AgentReply>(`/tickets/${ticketId}/run`, { method: 'POST', body: '{}' }),

  getEvents: (limit = 40) => request<AgentEvent[]>(`/events?limit=${limit}`),

  approvePayment: (body: {
    kind: string
    ref_id: number
    amount: number
    account: string
    approved_by: string
  }) =>
    request<ApprovePaymentResult>('/payments/approve', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  getCash: () => request<CashBalance>('/cash'),

  reset: () => request<ResetResult>('/reset', { method: 'POST' }),
}
