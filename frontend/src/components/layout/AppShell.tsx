import React, { useEffect, useState } from 'react';
import apiClient from '../../api/client';

export function AppShell({ children }: { children: React.ReactNode }) {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'unreachable'>('checking');

  useEffect(() => {
    apiClient
      .get('/api/v1/health')
      .then(() => setBackendStatus('connected'))
      .catch(() => setBackendStatus('unreachable'));
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-slate-900 text-white">
      <header className="sticky top-0 z-10 border-b border-slate-800 bg-slate-900/80 px-6 py-4 backdrop-blur">
        <h1 className="text-2xl font-bold tracking-tight">
          Geo<span className="text-blue-400">AI</span>
        </h1>
      </header>

      <main className="flex-grow p-6">
        <div className="mx-auto max-w-2xl">
          {children}
        </div>
      </main>

      <footer className="border-t border-slate-800 p-4 text-center">
        <div className="inline-flex items-center space-x-2 rounded-full bg-slate-800/50 px-3 py-1 text-xs">
          <span
            className={`h-2 w-2 rounded-full ${
              backendStatus === 'connected'
                ? 'bg-emerald-400'
                : backendStatus === 'unreachable'
                  ? 'bg-red-400'
                  : 'bg-yellow-400'
            }`}
          ></span>
          <span className="text-slate-400">
            {backendStatus === 'checking' && 'Checking backend...'}
            {backendStatus === 'connected' && 'Backend: connected'}
            {backendStatus === 'unreachable' && 'Backend: unreachable'}
          </span>
        </div>
      </footer>
    </div>
  );
}
