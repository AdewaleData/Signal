import { Button } from "./Button";

export function LoadingState({ label = "Checking…" }: { label?: string }) {
  return (
    <div className="px-5 py-16 text-center" role="status" aria-live="polite">
      <div className="mx-auto mb-4 h-8 w-8 animate-pulse rounded-full border-2 border-line border-t-forest" />
      <p className="text-sm text-muted">{label}</p>
    </div>
  );
}

export function ErrorState({
  message = "Could not refresh.",
  onRetry,
}: {
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="px-5 py-16 text-center" role="alert">
      <p className="mb-4 text-[15px] text-ink">{message}</p>
      {onRetry ? (
        <Button onClick={onRetry} className="mx-auto max-w-40">
          Try again
        </Button>
      ) : null}
    </div>
  );
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-2xl border border-line bg-white px-4 py-8 text-center">
      <p className="font-medium text-ink">{title}</p>
      <p className="mt-2 text-sm text-muted">{body}</p>
    </div>
  );
}
