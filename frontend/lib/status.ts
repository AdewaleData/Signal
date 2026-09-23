import type { RouteState } from "@/types";

export const STATE_COPY: Record<
  RouteState,
  { label: string; tone: string; surface: string; text: string; bar: string }
> = {
  CLEAR: {
    label: "Clear",
    tone: "text-clear",
    surface: "bg-emerald-50 border-emerald-200",
    text: "text-clear",
    bar: "bg-clear",
  },
  CAUTION: {
    label: "Caution",
    tone: "text-caution",
    surface: "bg-amber-50 border-amber-200",
    text: "text-caution",
    bar: "bg-caution",
  },
  AVOID: {
    label: "Avoid",
    tone: "text-avoid",
    surface: "bg-red-50 border-red-200",
    text: "text-avoid",
    bar: "bg-avoid",
  },
  UNKNOWN: {
    label: "Unknown",
    tone: "text-unknown",
    surface: "bg-slate-50 border-slate-200",
    text: "text-unknown",
    bar: "bg-unknown",
  },
};

export function percent(value: number) {
  return `${Math.round(value * 100)}%`;
}

export function incidentLabel(type: string) {
  const labels: Record<string, string> = {
    road_blocked: "Road blocked",
    crowd_gathering: "Crowd / gathering",
    accident: "Accident",
    fire: "Fire",
    security_incident: "Security incident",
    other: "Other",
    all_clear: "Road appears clear",
  };
  return labels[type] || type;
}

export function routePhrase(origin: string, destination: string) {
  return `${origin} to ${destination}`;
}

export function destinationToRoute(destination: string): string {
  const map: Record<string, string> = {
    Home: "shop-home",
    "Bus Station": "station-road",
    "Community Centre": "central-avenue",
    School: "hill-road",
    Market: "shop-home",
  };
  return map[destination] || "shop-home";
}
