import React from 'react';

interface EmptyStateProps {
  message: string;
}

export function EmptyState({ message }: EmptyStateProps) {
  return (
    <div className="p-8 text-center text-slate-400">
      <p>{message}</p>
    </div>
  );
}
