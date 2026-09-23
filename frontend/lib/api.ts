import type { Assessment, Evidence, Profile, Report, RouteSummary } from "@/types";

function apiBase() {
  const raw = process.env.NEXT_PUBLIC_API_URL;
  if (!raw) {
    return "";
  }
  if (raw.startsWith("http://") || raw.startsWith("https://")) {
    return raw.replace(/\/$/, "");
  }
  return `https://${raw.replace(/\/$/, "")}`;
}

const API = apiBase();

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers || {}),
      },
      cache: "no-store",
    });
  } catch {
    throw new ApiError("Could not refresh.");
  }

  if (!response.ok) {
    throw new ApiError("Could not refresh.", response.status);
  }
  return response.json() as Promise<T>;
}

export function getRoutes() {
  return request<{ routes: RouteSummary[]; destinations: string[] }>("/api/routes");
}

export function getRoute(id: string) {
  return request<RouteSummary>(`/api/routes/${id}`);
}

export function getAssessment(id: string) {
  return request<Assessment>(`/api/routes/${id}/assessment`);
}

export function getEvidence(id: string) {
  return request<Evidence>(`/api/routes/${id}/evidence`);
}

export function getReports() {
  return request<Report[]>("/api/reports");
}

export function getMe() {
  return request<Profile>("/api/me");
}

export function createReport(body: {
  incident_type: string;
  description: string;
  location_name: string;
  raw_text?: string;
}) {
  return request<Report>("/api/reports", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function simulateReport() {
  return request<{ assessment: Assessment }>("/api/demo/simulate-report", { method: "POST" });
}

export function contradictReport() {
  return request<{ assessment: Assessment }>("/api/demo/contradict-report", { method: "POST" });
}

export function resetDemo() {
  return request<{ assessment: Assessment }>("/api/demo/reset", { method: "POST" });
}
