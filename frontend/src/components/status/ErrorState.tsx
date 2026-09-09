
interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="rounded-lg border border-red-900/50 bg-red-950/20 p-6 text-center">
      <p className="mb-4 text-red-400">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="rounded bg-red-900/50 px-4 py-2 text-sm text-red-200 transition-colors hover:bg-red-800/50"
        >
          Try Again
        </button>
      )}
    </div>
  );
}
