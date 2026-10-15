export type AgentRole =
  | 'boss'
  | 'inventory'
  | 'accounting'
  | 'facilities'
  | 'customer_service'

export interface TicketSummary {
  id: number
  type: string
  subject: string
  requester: string
  status: string
  is_open: boolean
}

export interface PaymentProposal {
  kind: string
  ref_id: number
  amount: number
  account: string
  reason: string | null
}

export interface AgentReply {
  summary: string
  resolved: boolean
  partial_fulfillment_note: string | null
  needs_human_approval: boolean
  delegated_to: AgentRole[]
  payment_proposal: PaymentProposal | null
}

export interface AgentEvent {
  time: string
  agent: AgentRole
  delegation_trail: string[]
  input: string
  said: string
  tools_used: string[]
  resolved: boolean
}

export interface ApprovePaymentResult {
  success: boolean
  reason: string | null
  payment_id: number | null
  new_balance: number | null
}

export interface CashBalance {
  account: string
  balance: number
  date: string
}

export interface ResetResult {
  reset: boolean
  message: string
}
