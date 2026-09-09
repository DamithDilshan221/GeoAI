import React from 'react';

interface EmptyStateProps {
  message: string;
  children?: React.ReactNode;
}

export function EmptyState({ message, children }: EmptyStateProps) {
  return (
    <div className="p-8 text-center text-slate-400">
      <p>{message}</p>
      {children && <div className="mt-4">{children}</div>}
    </div>
  );
}
