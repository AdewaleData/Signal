"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/StateViews";
import { getReports } from "@/lib/api";
import { incidentLabel } from "@/lib/status";
import type { Report } from "@/types";

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    getReports()
      .then(setReports)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <AppShell>
      <div className="safe-bottom px-5 pb-8 pt-6">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Reports</h1>
            <p className="mt-1 text-sm text-muted">Latest local reports.</p>
          </div>
        </div>
        <div className="mt-5">
          <Button href="/reports/new">New report</Button>
        </div>
        {loading ? <LoadingState /> : null}
        {error ? <ErrorState message={error} onRetry={load} /> : null}
        {!loading && !error && reports.length === 0 ? (
          <div className="mt-6">
            <EmptyState title="No reports yet" body="New reports will show up here." />
          </div>
        ) : null}
        <ul className="mt-5 space-y-3">
          {reports.map((report) => (
            <li key={report.id} className="rounded-2xl border border-line bg-white p-4">
              <p className="text-xs font-medium text-muted">
                {incidentLabel(report.incident_type)}
              </p>
              <p className="mt-1 font-medium">{report.location_name}</p>
              <p className="mt-2 text-sm leading-6 text-ink">{report.description}</p>
              <p className="mt-3 text-sm text-muted">
                {report.user_role},{" "}
                {new Date(report.created_at).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })}
              </p>
            </li>
          ))}
        </ul>
      </div>
    </AppShell>
  );
}
