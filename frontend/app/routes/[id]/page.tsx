"use client";

import dynamic from "next/dynamic";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/Button";
import { BackLink } from "@/components/ui/BackLink";
import { ErrorState, LoadingState } from "@/components/ui/StateViews";
import { ConfidenceMeter } from "@/components/status/ConfidenceMeter";
import { StatusDot } from "@/components/status/StatusBadge";
import { DemoControls } from "@/components/demo/DemoControls";
import { getAssessment, getRoute } from "@/lib/api";
import { routePhrase, STATE_COPY } from "@/lib/status";
import type { Assessment, RouteSummary } from "@/types";

const RouteMap = dynamic(() => import("@/components/map/RouteMap").then((mod) => mod.RouteMap), {
  ssr: false,
});

export default function AssessmentPage() {
  const params = useParams<{ id: string }>();
  const id = params.id;
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [route, setRoute] = useState<RouteSummary | null>(null);
  const [alternate, setAlternate] = useState<RouteSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    setError(null);
    Promise.all([getAssessment(id), getRoute(id)])
      .then(async ([data, current]) => {
        setAssessment(data);
        setRoute(current);
        if (data.alternate_route_id) {
          setAlternate(await getRoute(data.alternate_route_id));
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
    const timer = setInterval(() => {
      getAssessment(id)
        .then(setAssessment)
        .catch(() => undefined);
    }, 15000);
    return () => clearInterval(timer);
  }, [id]);

  return (
    <AppShell>
      <div className="safe-bottom px-5 pb-8 pt-5">
        <BackLink href="/home">Back</BackLink>

        {loading ? <LoadingState /> : null}
        {error ? <ErrorState message={error} onRetry={load} /> : null}

        {assessment && !loading && !error ? (
          <div className="mt-5 grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
            <div>
              <p className="text-lg font-semibold">
                {routePhrase(assessment.origin, assessment.destination)}
              </p>
              <p className="mt-1 text-sm text-muted">
                {assessment.estimated_minutes} min, {assessment.distance_km} km
              </p>

              <section
                className={`mt-5 rounded-2xl border p-5 ${STATE_COPY[assessment.state].surface}`}
                aria-live="polite"
              >
                <p className={`flex items-center gap-2 text-lg font-semibold ${STATE_COPY[assessment.state].text}`}>
                  <StatusDot state={assessment.state} />
                  {assessment.headline}
                </p>
                <p className="mt-3 text-[15px] leading-6 text-ink">{assessment.reason}</p>
                {assessment.state !== "UNKNOWN" ? (
                  <div className="mt-5">
                    <ConfidenceMeter value={assessment.confidence} state={assessment.state} />
                  </div>
                ) : (
                  <p className="mt-4 text-sm text-muted">
                    Not enough evidence for a confidence score.
                  </p>
                )}
                <p className="mt-3 text-sm text-muted">
                  {assessment.updated_label ? `Updated ${assessment.updated_label}` : "No recent updates"}
                </p>
              </section>

              <div className="mt-4 space-y-3">
                <Button href={`/routes/${id}/evidence`}>Why this decision?</Button>
                {assessment.alternate_route_id ? (
                  <Button href={`/routes/${id}/alternate`} variant="secondary">
                    Alternate route
                  </Button>
                ) : null}
              </div>

              <dl className="mt-6 grid grid-cols-3 gap-2 text-center">
                <Metric label="Reports" value={String(assessment.recent_reports)} />
                <Metric label="Sources" value={String(assessment.independent_sources)} />
                <Metric label="Official" value={assessment.official_confirmation ? "Yes" : "None"} />
              </dl>

              {id === "shop-home" ? (
                <div className="mt-6">
                  <DemoControls
                    onChange={(next) => {
                      setAssessment(next);
                    }}
                  />
                </div>
              ) : null}
            </div>

            <div>
              {route ? (
                <RouteMap
                  primary={route}
                  alternate={alternate}
                  primaryState={assessment.state}
                  alternateState={alternate?.state}
                />
              ) : null}
            </div>
          </div>
        ) : null}
      </div>
    </AppShell>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-line bg-white px-2 py-3">
      <dt className="text-[11px] text-muted">{label}</dt>
      <dd className="mt-1 text-lg font-semibold">{value}</dd>
    </div>
  );
}
