"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ErrorState, LoadingState } from "@/components/ui/StateViews";
import { StatusBadge } from "@/components/status/StatusBadge";
import { getRoutes } from "@/lib/api";
import { percent, routePhrase } from "@/lib/status";
import type { RouteSummary } from "@/types";

export default function RoutesPage() {
  const [routes, setRoutes] = useState<RouteSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    getRoutes()
      .then((data) => setRoutes(data.routes.filter((route) => !route.alternate_of)))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <AppShell>
      <div className="safe-bottom px-5 pb-8 pt-6">
        <h1 className="text-2xl font-semibold tracking-tight">Routes</h1>
        <p className="mt-1 text-sm text-muted">Your saved paths.</p>
        {loading ? <LoadingState /> : null}
        {error ? <ErrorState message={error} onRetry={load} /> : null}
        <ul className="mt-5 space-y-3">
          {routes.map((route) => (
            <li key={route.id}>
              <Link href={`/routes/${route.id}`} className="block rounded-2xl border border-line bg-white p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-medium">{route.name}</p>
                    <p className="mt-1 text-sm text-muted">
                      {routePhrase(route.origin, route.destination)}
                    </p>
                    <p className="mt-1 text-sm text-muted">
                      {route.estimated_minutes} min, {route.distance_km} km
                    </p>
                  </div>
                  {route.state ? <StatusBadge state={route.state} compact /> : null}
                </div>
                {route.confidence != null && route.state && route.state !== "UNKNOWN" ? (
                  <p className="mt-3 text-sm text-muted">Confidence {percent(route.confidence)}</p>
                ) : null}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </AppShell>
  );
}
