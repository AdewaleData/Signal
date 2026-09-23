"use client";

import { useEffect, useRef } from "react";
import maplibregl, { type Map as MapLibreMap, type Marker } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import type { RouteState, RouteSummary } from "@/types";

type Props = {
  primary: RouteSummary;
  alternate?: RouteSummary | null;
  primaryState?: RouteState | null;
  alternateState?: RouteState | null;
  highlight?: "primary" | "alternate" | "both";
};

const STYLE = "https://tiles.openfreemap.org/styles/positron";

export function RouteMap({
  primary,
  alternate,
  primaryState,
  alternateState,
  highlight = "both",
}: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const markersRef = useRef<Marker[]>([]);

  useEffect(() => {
    const node = containerRef.current;
    if (!node) return;

    const map = new maplibregl.Map({
      container: node,
      style: STYLE,
      center: centerOf(primary, alternate),
      zoom: 14.2,
      attributionControl: { compact: true },
    });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    mapRef.current = map;

    let cancelled = false;

    map.on("load", async () => {
      const primaryLine =
        highlight === "alternate" ? [] : await snapToRoads(primary.geometry);
      const altLine =
        alternate && highlight !== "primary" ? await snapToRoads(alternate.geometry) : [];
      if (cancelled) return;

      if (primaryLine.length) {
        addLine(map, "primary-route", primaryLine, strokeFor(primaryState, "primary"));
      }
      if (altLine.length) {
        addLine(map, "alternate-route", altLine, strokeFor(alternateState, "alternate"));
      }

      const bounds = new maplibregl.LngLatBounds();
      [...primaryLine, ...altLine].forEach(([lat, lng]) => bounds.extend([lng, lat]));
      if (!bounds.isEmpty()) {
        map.fitBounds(bounds, { padding: 48, maxZoom: 15.4, duration: 0 });
      }

      clearMarkers(markersRef.current);
      const start = primary.segments[0];
      const end = primary.segments[primary.segments.length - 1];
      const incident = primary.segments.find((segment) => segment.name === "Pharmacy") || primary.segments[1];

      if (start) {
        markersRef.current.push(placeMarker(map, start.latitude, start.longitude, primary.origin, "#0E4A38"));
      }
      if (end) {
        markersRef.current.push(placeMarker(map, end.latitude, end.longitude, primary.destination, "#0E4A38"));
      }
      if (incident && (primaryState === "CAUTION" || primaryState === "AVOID")) {
        markersRef.current.push(
          placeMarker(map, incident.latitude, incident.longitude, "Incident area", "#C23B2E"),
        );
      }
    });

    return () => {
      cancelled = true;
      clearMarkers(markersRef.current);
      markersRef.current = [];
      map.remove();
      mapRef.current = null;
    };
  }, [primary, alternate, primaryState, alternateState, highlight]);

  return (
    <figure className="overflow-hidden rounded-2xl border border-line bg-white">
      <div ref={containerRef} className="map-frame w-full" role="img" aria-label="Live map of the selected route" />
      <figcaption className="flex flex-wrap gap-x-4 gap-y-2 border-t border-line px-4 py-3 text-xs text-muted">
        <span>Usual</span>
        <span>Safer</span>
        <span>Incident</span>
      </figcaption>
    </figure>
  );
}

function addLine(map: MapLibreMap, id: string, points: number[][], color: string) {
  const source = {
    type: "geojson" as const,
    data: {
      type: "Feature" as const,
      properties: {},
      geometry: {
        type: "LineString" as const,
        coordinates: points.map(([lat, lng]) => [lng, lat]),
      },
    },
  };
  if (map.getSource(id)) {
    map.removeLayer(`${id}-line`);
    map.removeSource(id);
  }
  map.addSource(id, source);
  map.addLayer({
    id: `${id}-line`,
    type: "line",
    source: id,
    paint: {
      "line-color": color,
      "line-width": 5,
      "line-opacity": 0.92,
    },
    layout: {
      "line-cap": "round",
      "line-join": "round",
    },
  });
}

function placeMarker(map: MapLibreMap, lat: number, lng: number, label: string, color: string) {
  const el = document.createElement("div");
  el.className = "signal-marker";
  el.innerHTML = `<span class="signal-marker-dot" style="background:${color}"></span><span class="signal-marker-label">${label}</span>`;
  return new maplibregl.Marker({ element: el, anchor: "left" }).setLngLat([lng, lat]).addTo(map);
}

function clearMarkers(markers: Marker[]) {
  markers.forEach((marker) => marker.remove());
}

function centerOf(primary: RouteSummary, alternate?: RouteSummary | null): [number, number] {
  const points = [...primary.geometry, ...(alternate?.geometry || [])];
  const lat = points.reduce((sum, point) => sum + point[0], 0) / points.length;
  const lng = points.reduce((sum, point) => sum + point[1], 0) / points.length;
  return [lng, lat];
}

function strokeFor(state: RouteState | null | undefined, kind: "primary" | "alternate") {
  if (kind === "alternate") return "#1F7A4D";
  if (state === "AVOID" || state === "CAUTION") return "#C23B2E";
  if (state === "CLEAR") return "#1F7A4D";
  return "#6B7280";
}

async function snapToRoads(points: number[][]): Promise<number[][]> {
  if (points.length < 2) return points;
  const coords = points.map(([lat, lng]) => `${lng},${lat}`).join(";");
  try {
    const response = await fetch(
      `https://router.project-osrm.org/route/v1/driving/${coords}?overview=full&geometries=geojson`,
    );
    if (!response.ok) return points;
    const data = await response.json();
    const line = data.routes?.[0]?.geometry?.coordinates;
    if (!line?.length) return points;
    return line.map(([lng, lat]: [number, number]) => [lat, lng]);
  } catch {
    return points;
  }
}
