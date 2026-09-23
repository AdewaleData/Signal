"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { BackLink } from "@/components/ui/BackLink";
import { Button } from "@/components/ui/Button";
import { ErrorState, LoadingState } from "@/components/ui/StateViews";
import { ConfidenceMeter } from "@/components/status/ConfidenceMeter";
import { StatusBadge } from "@/components/status/StatusBadge";
import { getEvidence } from "@/lib/api";
import { percent } from "@/lib/status";
import type { Evidence, EvidenceItem } from "@/types";

export default function EvidencePage() {
  const params = useParams<{ id: string }>();
  const [data, setData] = useState<Evidence | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    getEvidence(params.id)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, [params.id]);

  return (
    <AppShell>
      <div className="safe-bottom px-5 pb-8 pt-5">
        <div className="flex items-center justify-between">
          <BackLink href={`/routes/${params.id}`}>Back</BackLink>
          {data ? <StatusBadge state={data.state} compact /> : null}
        </div>

        {loading ? <LoadingState /> : null}
        {error ? <ErrorState message={error} onRetry={load} /> : null}

        {data && !loading && !error ? (
          <>
            <h1 className="mt-5 text-2xl font-semibold tracking-tight">Why this decision?</h1>
            <section className="mt-5 rounded-2xl border border-line bg-white p-4">
              {data.state === "UNKNOWN" ? (
                <p className="text-sm text-muted">Not enough evidence for a score.</p>
              ) : (
                <ConfidenceMeter value={data.confidence} state={data.state} />
              )}
              <p className="mt-3 text-sm text-muted">From the reports we have.</p>
            </section>

            <h2 className="mt-7 text-lg font-semibold">Factors</h2>
            <ul className="mt-3 space-y-2">
              {data.factors
                .filter((factor) => factor.key !== "contradiction" || factor.warning)
                .map((factor) => (
                  <li key={factor.key} className="flex items-start gap-3 rounded-2xl border border-line bg-white p-4">
                    <span
                      className={`mt-0.5 shrink-0 text-xs font-medium ${
                        factor.met ? "text-clear" : "text-caution"
                      }`}
                    >
                      {factor.met ? "Met" : "Missing"}
                    </span>
                    <div>
                      <p className="font-medium">{factor.label}</p>
                      <p className="text-sm text-muted">{factor.detail}</p>
                    </div>
                  </li>
                ))}
            </ul>

            <h2 className="mt-8 text-lg font-semibold">Reports</h2>
            {data.reports.length === 0 ? (
              <p className="mt-3 text-sm text-muted">No reports on this route.</p>
            ) : (
              <ol className="mt-3 space-y-3">
                {data.reports.map((report) => (
                  <EvidenceCard key={report.id} report={report} />
                ))}
              </ol>
            )}

            {data.conflicting.length > 0 ? (
              <>
                <h2 className="mt-8 text-lg font-semibold text-caution">Conflicts</h2>
                <p className="mt-1 text-sm text-muted">These reports disagree.</p>
                <ol className="mt-3 space-y-3">
                  {data.conflicting.map((report) => (
                    <EvidenceCard key={report.id} report={report} conflict />
                  ))}
                </ol>
              </>
            ) : null}

            <section className="mt-8 rounded-2xl border border-line bg-white p-4">
              <h3 className="font-medium">What is confidence?</h3>
              <p className="mt-2 text-sm leading-6 text-muted">{data.disclaimer}</p>
            </section>

            <div className="mt-5">
              <Button href={`/routes/${params.id}`}>Got it</Button>
            </div>
          </>
        ) : null}
      </div>
    </AppShell>
  );
}

function EvidenceCard({ report, conflict = false }: { report: EvidenceItem; conflict?: boolean }) {
  const time = new Date(report.created_at).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  return (
    <li className={`rounded-2xl border p-4 ${conflict ? "border-amber-200 bg-amber-50" : "border-line bg-white"}`}>
      <p className="text-xs font-medium text-muted">
        {conflict ? "Conflict" : `Report ${String(report.index).padStart(2, "0")}`}
      </p>
      <p className="mt-2 text-sm text-muted">
        {time}, {report.source_role}
      </p>
      <p className="mt-2 text-[15px] leading-6">&ldquo;{report.description}&rdquo;</p>
      <dl className="mt-3 grid grid-cols-2 gap-2 text-sm">
        <div>
          <dt className="text-muted">Reliability</dt>
          <dd>{percent(report.source_reliability)}</dd>
        </div>
        <div>
          <dt className="text-muted">Location</dt>
          <dd>{report.location_name}</dd>
        </div>
        <div>
          <dt className="text-muted">Status</dt>
          <dd>{report.status}</dd>
        </div>
        <div>
          <dt className="text-muted">Source</dt>
          <dd>{report.source_name}</dd>
        </div>
      </dl>
    </li>
  );
}
