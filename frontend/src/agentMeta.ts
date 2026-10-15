import type { AgentRole } from './types'

export interface AgentMeta {
  role: AgentRole
  label: string
  blurb: string
  color: string
  glow: string
  glyph: string
}

export const AGENT_ORDER: AgentRole[] = [
  'boss',
  'inventory',
  'accounting',
  'facilities',
  'customer_service',
]

export const AGENT_META: Record<AgentRole, AgentMeta> = {
  boss: {
    role: 'boss',
    label: 'BOSS',
    blurb: 'Reads every ticket, delegates, makes the final call',
    color: '#00356b',
    glow: '#3b78c2',
    glyph: '♛',
  },
  inventory: {
    role: 'inventory',
    label: 'INVENTORY',
    blurb: 'Stock, shortfalls, vendor restocks',
    color: '#0f7a4a',
    glow: '#3fbf86',
    glyph: '▣',
  },
  accounting: {
    role: 'accounting',
    label: 'ACCOUNTING',
    blurb: 'Cash, invoices, margins, payments',
    color: '#9a6a00',
    glow: '#e3ab2e',
    glyph: '$',
  },
  facilities: {
    role: 'facilities',
    label: 'FACILITIES',
    blurb: 'Leases and rent',
    color: '#6a3fa0',
    glow: '#b088e0',
    glyph: '⌂',
  },
  customer_service: {
    role: 'customer_service',
    label: 'CUSTOMER SERVICE',
    blurb: 'Drafts messages — never sends them',
    color: '#a23a5e',
    glow: '#e87fa4',
    glyph: '✉',
  },
}
