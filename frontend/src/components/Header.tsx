import { useEffect, useRef, useState } from 'react'

interface Props {
  balance: number | null
  onReset: () => void
  resetting: boolean
}

function useCountUp(target: number | null) {
  const [display, setDisplay] = useState(target ?? 0)
  const prev = useRef(target ?? 0)

  useEffect(() => {
    if (target === null) return
    const from = prev.current
    const to = target
    if (from === to) return
    const duration = 600
    const start = performance.now()

    let raf: number
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration)
      const eased = 1 - Math.pow(1 - t, 3)
      setDisplay(from + (to - from) * eased)
      if (t < 1) raf = requestAnimationFrame(tick)
      else prev.current = to
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [target])

  return display
}

export default function Header({ balance, onReset, resetting }: Props) {
  const shown = useCountUp(balance)
  const dropping = balance !== null && shown > balance + 0.5

  return (
    <header className="app-header">
      <div className="brand">
        <div className="brand-mark">CC</div>
        <div>
          <h1>Campus Customs</h1>
          <p className="brand-sub">Multi-Agent Operations Desk</p>
        </div>
      </div>

      <div className="header-right">
        <div className={`cash-meter ${dropping ? 'cash-meter--dropping' : ''}`}>
          <span className="cash-label">Checking balance</span>
          <span className="cash-value">
            ${shown.toLocaleString(undefined, { maximumFractionDigits: 0 })}
          </span>
        </div>
        <button className="btn btn-ghost" onClick={onReset} disabled={resetting}>
          {resetting ? 'Resetting…' : '↺ Reset Desk'}
        </button>
      </div>
    </header>
  )
}
