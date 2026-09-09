
interface PermissionDeniedStateProps {
  message: string;
  onRetry?: () => void;
}

export function PermissionDeniedState({ message, onRetry }: PermissionDeniedStateProps) {
  return (
    <div className="rounded-lg border border-orange-900/50 bg-orange-950/20 p-6 text-center">
      <h3 className="mb-2 text-lg font-semibold text-orange-400">Location Required</h3>
      <p className="mb-4 text-orange-300">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="rounded bg-orange-900/50 px-4 py-2 text-sm text-orange-200 transition-colors hover:bg-orange-800/50"
        >
          Try Again
        </button>
      )}
    </div>
  );
}
