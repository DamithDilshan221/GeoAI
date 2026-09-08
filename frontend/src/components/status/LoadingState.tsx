import React from 'react';

interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = 'Loading...' }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center text-slate-300">
      <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-slate-700 border-t-blue-500"></div>
      <p>{message}</p>
    </div>
  );
}
