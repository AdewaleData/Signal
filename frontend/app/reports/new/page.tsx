"use client";

import { useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { BackLink } from "@/components/ui/BackLink";
import { Button } from "@/components/ui/Button";
import { createReport } from "@/lib/api";

const INCIDENTS = [
  ["road_blocked", "Road blocked"],
  ["crowd_gathering", "Crowd / gathering"],
  ["accident", "Accident"],
  ["fire", "Fire"],
  ["security_incident", "Security incident"],
  ["other", "Other"],
];

const PLACES = ["Market Road", "Station Road", "Central Avenue", "River Road", "Hill Road", "Pharmacy", "Bus Station"];

export default function ReportPage() {
  const [incident, setIncident] = useState("road_blocked");
  const [location, setLocation] = useState("Market Road");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await createReport({
        incident_type: incident,
        location_name: location,
                description: description || "Activity seen here.",
        raw_text: description || undefined,
      });
      setDone(true);
    } catch {
      setError("Could not send. Try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <div className="safe-bottom px-5 pb-8 pt-5">
        <BackLink href="/reports">Back</BackLink>

        {done ? (
          <section className="mt-8 rounded-2xl border border-line bg-white p-5">
            <h1 className="text-2xl font-semibold">Report received.</h1>
            <p className="mt-3 text-[15px] leading-6 text-muted">
              We will compare it with other reports. Not verified yet.
            </p>
            <div className="mt-6 space-y-3">
              <Button href="/routes/shop-home">Check route</Button>
              <Button href="/reports" variant="secondary">
                All reports
              </Button>
            </div>
          </section>
        ) : (
          <form onSubmit={onSubmit} className="mt-6">
            <h1 className="text-2xl font-semibold tracking-tight">What happened?</h1>
            <fieldset className="mt-5 space-y-2">
              <legend className="sr-only">Incident type</legend>
              {INCIDENTS.map(([value, label]) => (
                <label
                  key={value}
                  className={`flex min-h-12 items-center gap-3 rounded-xl border bg-white px-4 ${
                    incident === value ? "border-forest" : "border-line"
                  }`}
                >
                  <input
                    type="radio"
                    name="incident"
                    value={value}
                    checked={incident === value}
                    onChange={() => setIncident(value)}
                    className="accent-forest"
                  />
                  {label}
                </label>
              ))}
            </fieldset>

            <label className="mt-6 block text-sm font-medium" htmlFor="location">
              Where?
            </label>
            <div className="mt-2 flex gap-2">
              <select
                id="location"
                className="min-h-12 flex-1 rounded-xl border border-line bg-white px-3"
                value={location}
                onChange={(event) => setLocation(event.target.value)}
              >
                {PLACES.map((place) => (
                  <option key={place}>{place}</option>
                ))}
              </select>
              <button
                type="button"
                className="min-h-12 rounded-xl border border-line px-3 text-sm"
                onClick={() => setLocation("Market Road")}
              >
                Use area
              </button>
            </div>

            <label className="mt-6 block text-sm font-medium" htmlFor="observed">
              What did you see?
            </label>
            <textarea
              id="observed"
              className="mt-2 min-h-28 w-full rounded-xl border border-line bg-white p-3 text-[15px]"
              placeholder="Vehicles cannot pass near the market. People are gathered around the area."
              value={description}
              onChange={(event) => setDescription(event.target.value)}
            />

            {error ? (
              <p className="mt-3 text-sm text-avoid" role="alert">
                {error}
              </p>
            ) : null}

            <div className="mt-5">
              <Button type="submit" disabled={submitting}>
                {submitting ? "Sending…" : "Submit report"}
              </Button>
            </div>
          </form>
        )}
      </div>
    </AppShell>
  );
}
