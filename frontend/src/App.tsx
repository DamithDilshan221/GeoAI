import { useEffect, useState } from 'react'
import { Route, Routes } from 'react-router-dom'
import apiClient from './api/client'

function HomePage() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'unreachable'>(
    'checking',
  )

  useEffect(() => {
    apiClient
      .get('/api/v1/health')
      .then(() => setBackendStatus('connected'))
      .catch(() => setBackendStatus('unreachable'))
  }, [])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white">
      <h1 className="mb-4 text-5xl font-bold tracking-tight">
        Geo<span className="text-blue-400">AI</span>
      </h1>
      <p className="mb-8 text-lg text-slate-300">
        Intelligent Facility Finder &amp; Smart Navigation
      </p>
      <div className="rounded-xl border border-slate-700 bg-slate-800/50 px-8 py-6 shadow-lg backdrop-blur">
        <p className="text-sm text-slate-400">System Status</p>
        <p
          className={`mt-2 text-lg font-semibold ${
            backendStatus === 'connected'
              ? 'text-emerald-400'
              : backendStatus === 'unreachable'
                ? 'text-red-400'
                : 'text-yellow-400'
          }`}
        >
          {backendStatus === 'checking' && 'Checking backend...'}
          {backendStatus === 'connected' && 'Backend: connected'}
          {backendStatus === 'unreachable' && 'Backend: unreachable'}
        </p>
      </div>
      <p className="mt-12 text-xs text-slate-500">Phase 1 of 20 — Project Foundation</p>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
    </Routes>
  )
}
