"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/Button";
import { ErrorState, LoadingState } from "@/components/ui/StateViews";
import { StatusBadge } from "@/components/status/StatusBadge";
import { getMe, getRoutes } from "@/lib/api";
import { destinationToRoute, routePhrase } from "@/lib/status";
import type { Profile, RouteSummary } from "@/types";

export default function HomePage() {
  const [routes, setRoutes] = useState<RouteSummary[]>([]);
  const [profile, setProfile] = useState<Profile | null>(null);
  const [destination, setDestination] = useState("Home");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  function load() {
    setLoading(true);
    setError(null);
    Promise.all([getRoutes(), getMe()])
      .then(([routeData, me]) => {
        setRoutes(routeData.routes);
        setProfile(me);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    load();
  }, []);

  const destinations = useMemo(() => {
    const values = Array.from(new Set(routes.map((route) => route.destination)));
    return values.length ? values : ["Home"];
  }, [routes]);

  const recent = routes.filter((route) => !route.alternate_of);

  return (
    <AppShell>
      <header className="flex items-center justify-between px-5 pb-2 pt-6">
        <Logo />
        <Link
          href="/profile"
          className="flex h-9 w-9 items-center justify-center rounded-full bg-forest text-xs font-semibold text-white"
          aria-label="Open profile"
        >
          {profile?.name.slice(0, 1) || "A"}
        </Link>
      </header>

      <div className="safe-bottom px-5 pb-8 pt-6">
        {loading ? <LoadingState /> : null}
        {error ? <ErrorState message={error} onRetry={load} /> : null}

        {!loading && !error ? (
          <>
            <h1 className="text-[28px] font-semibold leading-tight tracking-tight">Where are you going?</h1>
            <p className="mt-2 text-[15px] text-muted">Latest status for your route.</p>

            <label className="mt-6 block text-sm font-medium text-ink" htmlFor="destination">
              Destination
            </label>
            <select
              id="destination"
              className="mt-2 min-h-12 w-full rounded-xl border border-line bg-white px-3 text-[15px]"
              value={destination}
              onChange={(event) => setDestination(event.target.value)}
            >
              {destinations.map((item) => (
                <option key={item}>{item}</option>
              ))}
            </select>

            <div className="mt-4">
              <Button href={`/routes/${destinationToRoute(destination)}`}>Check route</Button>
            </div>

            <section className="mt-8">
              <h2 className="text-sm font-medium text-muted">Quick</h2>
              <div className="mt-3 grid grid-cols-4 gap-2">
                <Quick href="/routes" label="Routes" />
                <Quick href="/reports/new" label="Report" />
                <Quick href="/reports" label="Signals" />
                <Quick href="/profile" label="Profile" />
              </div>
            </section>

            <section className="mt-8">
              <div className="flex items-center justify-between">
                <h2 className="text-[17px] font-semibold">Recent signals</h2>
                <Link href="/routes" className="text-sm text-forest">
                  View all
                </Link>
              </div>
              <ul className="mt-3 space-y-2">
                {recent.map((route) => (
                  <li key={route.id}>
                    <Link
                      href={`/routes/${route.id}`}
                      className="flex items-center justify-between rounded-2xl border border-line bg-white px-4 py-3"
                    >
                      <div>
                        <p className="font-medium text-ink">{route.name}</p>
                        <p className="text-sm text-muted">
                          {routePhrase(route.origin, route.destination)}
                        </p>
                      </div>
                      {route.state ? <StatusBadge state={route.state} compact /> : null}
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          </>
        ) : null}
      </div>
    </AppShell>
  );
}

function Quick({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="flex min-h-[76px] flex-col items-center justify-center rounded-2xl border border-line bg-white px-1 text-center text-[11px] leading-4 text-ink"
    >
      {label}
    </Link>
  );
}
