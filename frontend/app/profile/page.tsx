"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { ErrorState, LoadingState } from "@/components/ui/StateViews";
import { getMe } from "@/lib/api";
import { percent } from "@/lib/status";
import type { Profile } from "@/types";

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMe()
      .then(setProfile)
      .catch((err) => setError(err.message));
  }, []);

  return (
    <AppShell>
      <div className="safe-bottom px-5 pb-8 pt-6">
        <h1 className="text-2xl font-semibold tracking-tight">Profile</h1>
        {!profile && !error ? <LoadingState label="Loading…" /> : null}
        {error ? <ErrorState message={error} /> : null}
        {profile ? (
          <section className="mt-6 rounded-2xl border border-line bg-white p-5">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-forest text-lg font-semibold text-white">
                {profile.name.slice(0, 1)}
              </div>
              <div>
                <p className="font-semibold">{profile.name}</p>
                <p className="text-sm text-muted">
                  {profile.role}, {profile.town}
                </p>
              </div>
            </div>
            <p className="mt-4 text-sm text-muted">
              Reliability {percent(profile.reliability_score)}. Demo score.
            </p>
          </section>
        ) : null}

        <ul className="mt-5 space-y-2">
          <li>
            <Link href="/how-it-works" className="block rounded-2xl border border-line bg-white px-4 py-4">
              How it works
            </Link>
          </li>
          <li>
            <Link href="/" className="block rounded-2xl border border-line bg-white px-4 py-4">
              Welcome
            </Link>
          </li>
        </ul>

        <p className="mt-8 text-sm leading-6 text-muted">
          Not a safety guarantee. Not emergency services. Demo people are fictional.
        </p>
      </div>
    </AppShell>
  );
}
