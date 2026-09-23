import type { RouteState } from "@/types";
import { STATE_COPY } from "@/lib/status";

export function StatusBadge({ state, compact = false }: { state: RouteState; compact?: boolean }) {
  const copy = STATE_COPY[state];
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium ${copy.surface} ${copy.text}`}
    >
      <StatusDot state={state} />
      <span>{compact ? shortLabel(state) : copy.label}</span>
    </span>
  );
}

export function StatusDot({ state }: { state: RouteState }) {
  const copy = STATE_COPY[state];
  return <span className={`inline-block h-2 w-2 rounded-full ${copy.bar}`} aria-hidden="true" />;
}

function shortLabel(state: RouteState) {
  return {
    CLEAR: "Clear",
    CAUTION: "Use caution",
    AVOID: "Avoid",
    UNKNOWN: "Unknown",
  }[state];
}
