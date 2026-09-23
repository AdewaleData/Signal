export type RouteState = "CLEAR" | "CAUTION" | "AVOID" | "UNKNOWN";

export type RoutePoint = {
  name: string;
  latitude: number;
  longitude: number;
  sequence: number;
};

export type RouteSummary = {
  id: string;
  name: string;
  origin: string;
  destination: string;
  estimated_minutes: number;
  distance_km: number;
  alternate_of: string | null;
  geometry: number[][];
  segments: RoutePoint[];
  state: RouteState | null;
  confidence: number | null;
};

export type Factor = {
  key: string;
  label: string;
  detail: string;
  met: boolean;
  warning: boolean;
  score: number;
};

export type EvidenceItem = {
  id: string;
  index: number;
  created_at: string;
  source_name: string;
  source_role: string;
  description: string;
  source_reliability: number;
  location_name: string;
  status: string;
  incident_type: string;
  conflicting: boolean;
};

export type Assessment = {
  route_id: string;
  route_name: string;
  origin: string;
  destination: string;
  estimated_minutes: number;
  distance_km: number;
  state: RouteState;
  headline: string;
  reason: string;
  confidence: number;
  last_updated: string | null;
  updated_label: string | null;
  freshness_label: string;
  recent_reports: number;
  independent_sources: number;
  official_confirmation: boolean;
  cluster_location: string | null;
  alternate_route_id: string | null;
};

export type Evidence = Assessment & {
  factors: Factor[];
  reports: EvidenceItem[];
  conflicting: EvidenceItem[];
  disclaimer: string;
};

export type Report = {
  id: string;
  user_id: string;
  user_name: string;
  user_role: string;
  incident_type: string;
  description: string;
  latitude: number;
  longitude: number;
  location_name: string;
  created_at: string;
  status: string;
  severity: string;
  source_reliability: number;
  evidence_quality: number;
  is_official: boolean;
};

export type Profile = {
  id: string;
  name: string;
  role: string;
  town: string;
  reliability_score: number;
};
