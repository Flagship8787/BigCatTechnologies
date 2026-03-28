import { useEffect, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000'

type Status = 'loading' | 'ok' | 'error'

export function HealthCheck() {
  const [status, setStatus] = useState<Status>('loading')
  const [detail, setDetail] = useState<string>('')

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => {
        setStatus(res.ok ? 'ok' : 'error')
        setDetail(`HTTP ${res.status}`)
      })
      .catch((err) => {
        setStatus('error')
        setDetail(err.message)
      })
  }, [])

  const color = status === 'ok' ? '#22c55e' : status === 'error' ? '#ef4444' : '#f59e0b'

  return (
    <div className="health-check">
      <h2>API Health</h2>
      <p>
        <span className="health-dot" style={{ background: color }} />
        <strong>{status.toUpperCase()}</strong>
        {detail && <span className="health-detail"> — {detail}</span>}
      </p>
      <p className="health-url">Endpoint: {API_URL}/health</p>
    </div>
  )
}
