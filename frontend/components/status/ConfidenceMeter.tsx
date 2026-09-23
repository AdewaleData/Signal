import { percent, STATE_COPY } from "@/lib/status";
import type { RouteState } from "@/types";

export function ConfidenceMeter({ value, state }: { value: number; state: RouteState }) {
  const width = Math.max(0, Math.min(100, Math.round(value * 100)));
  return (
    <div>
      <div className="mb-2 flex items-center justify-between text-sm">
        <span className="text-muted">Confidence</span>
        <span className="font-semibold text-ink">{percent(value)}</span>
      </div>
      <div
        className="h-2 overflow-hidden rounded-full bg-slate-200"
        role="meter"
        aria-label="Confidence"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={width}
      >
        <div className={`h-full rounded-full ${STATE_COPY[state].bar}`} style={{ width: `${width}%` }} />
      </div>
    </div>
  );
}
