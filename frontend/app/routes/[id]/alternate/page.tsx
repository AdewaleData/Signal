"use client";

import dynamic from "next/dynamic";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { BackLink } from "@/components/ui/BackLink";
import { Button } from "@/components/ui/Button";
import { ErrorState, LoadingState } from "@/components/ui/StateViews";
import { StatusBadge } from "@/components/status/StatusBadge";
import { getAssessment, getRoute } from "@/lib/api";
import { routePhrase } from "@/lib/status";
import type { Assessment, RouteSummary } from "@/types";

const RouteMap = dynamic(() => import("@/components/map/RouteMap").then((mod) => mod.RouteMap), {
  ssr: false,
});

export default function AlternatePage() {
  const params = useParams<{ id: string }>();
  const [current, setCurrent] = useState<RouteSummary | null>(null);
  const [alt, setAlt] = useState<RouteSummary | null>(null);
  const [currentAssessment, setCurrentAssessment] = useState<Assessment | null>(null);
  const [altAssessment, setAltAssessment] = useState<Assessment | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    getAssessment(params.id)
      .then(async (assessment) => {
        setCurrentAssessment(assessment);
        const route = await getRoute(params.id);
        setCurrent(route);
        if (!assessment.alternate_route_id) {
          throw new Error("No alternate route.");
        }
        const [altRoute, altAssess] = await Promise.all([
          getRoute(assessment.alternate_route_id),
          getAssessment(assessment.alternate_route_id),
        ]);
        setAlt(altRoute);
        setAltAssessment(altAssess);
      })
        .catch((err) => setError(err.message || "Could not refresh."))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, [params.id]);

  const extra =
    current && alt ? Math.max(0, alt.estimated_minutes - current.estimated_minutes) : 0;

  return (
    <AppShell>
      <div className="safe-bottom px-5 pb-8 pt-5">
        <BackLink href={`/routes/${params.id}`}>Back</BackLink>

        {loading ? <LoadingState /> : null}
        {error ? <ErrorState message={error} onRetry={load} /> : null}

        {current && alt && currentAssessment && altAssessment && !loading && !error ? (
          <>
            <p className="mt-4 text-lg font-semibold">
              {routePhrase(current.origin, current.destination)}
            </p>
            <p className="text-sm text-muted">
              {alt.estimated_minutes} min, {alt.distance_km} km
              {extra ? `, plus ${extra} min` : ""}
            </p>

            <div className="mt-5">
              <RouteMap
                primary={current}
                alternate={alt}
                primaryState={currentAssessment.state}
                alternateState={altAssessment.state}
                highlight="both"
              />
            </div>

            <div className="mt-5 grid gap-3">
              <Compare
                title="Usual route"
                route={current}
                state={currentAssessment.state}
                muted
              />
              <Compare title="Safer option" route={alt} state={altAssessment.state} />
            </div>

            <p className="mt-4 text-sm text-muted">
              {extra
                ? `Adds ${extra} minute${extra === 1 ? "" : "s"}.`
                : "Similar travel time."}
            </p>

            <div className="mt-5 space-y-3">
              <Button href={`/routes/${alt.id}`}>Use this route</Button>
              <Button href={`/routes/${params.id}`} variant="secondary">
                Back
              </Button>
            </div>
          </>
        ) : null}
      </div>
    </AppShell>
  );
}

function Compare({
  title,
  route,
  state,
  muted,
}: {
  title: string;
  route: RouteSummary;
  state: NonNullable<RouteSummary["state"]>;
  muted?: boolean;
}) {
  return (
    <div className={`rounded-2xl border p-4 ${muted ? "border-line bg-white" : "border-emerald-200 bg-emerald-50"}`}>
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm text-muted">{title}</p>
          <p className="font-medium">
            {route.name}, {route.estimated_minutes} min, {route.distance_km} km
          </p>
        </div>
        <StatusBadge state={state} compact />
      </div>
    </div>
  );
}
