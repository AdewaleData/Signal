"use client";

import { useState } from "react";
import { contradictReport, resetDemo, simulateReport } from "@/lib/api";
import type { Assessment } from "@/types";

export function DemoControls({
  onChange,
}: {
  onChange: (assessment: Assessment) => void;
}) {
  const [busy, setBusy] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);

  async function run(kind: "sim" | "con" | "reset") {
    setBusy(kind);
    setNote(null);
    try {
      const action = kind === "sim" ? simulateReport : kind === "con" ? contradictReport : resetDemo;
      const data = await action();
      onChange(data.assessment);
      setNote(kind === "sim" ? "Report added." : kind === "con" ? "Conflict added." : "Reset.");
    } catch {
      setNote("Could not update. Is the API running?");
    } finally {
      setBusy(null);
    }
  }

  return (
    <section className="rounded-2xl border border-line bg-white p-4">
      <p className="text-sm font-medium text-ink">Test evidence</p>
      <p className="mt-1 text-sm text-muted">Add a report and watch the status change.</p>
      <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-3">
        <button
          className="min-h-11 rounded-xl border border-line px-3 text-sm text-ink"
          onClick={() => run("sim")}
          disabled={!!busy}
        >
          {busy === "sim" ? "Adding…" : "Corroborate"}
        </button>
        <button
          className="min-h-11 rounded-xl border border-line px-3 text-sm text-ink"
          onClick={() => run("con")}
          disabled={!!busy}
        >
          {busy === "con" ? "Adding…" : "Contradict"}
        </button>
        <button
          className="min-h-11 rounded-xl border border-line px-3 text-sm text-ink"
          onClick={() => run("reset")}
          disabled={!!busy}
        >
          {busy === "reset" ? "Resetting…" : "Reset"}
        </button>
      </div>
      {note ? <p className="mt-3 text-sm text-forest">{note}</p> : null}
    </section>
  );
}
