import { Event, VesselTrack, SourceHealth, ReplayStatus } from "@/types/events";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchEvents(limit = 50, type?: string, severity?: string): Promise<Event[]> {
  const url = new URL(`${API_BASE}/events`);
  url.searchParams.set("limit", limit.toString());
  if (type) url.searchParams.set("type", type);
  if (severity) url.searchParams.set("severity", severity);
  
  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch events: ${res.statusText}`);
  return res.json();
}

export async function fetchEventById(id: string): Promise<Event> {
  const res = await fetch(`${API_BASE}/events/${id}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch event ${id}: ${res.statusText}`);
  return res.json();
}

export async function fetchVessels(): Promise<VesselTrack[]> {
  const res = await fetch(`${API_BASE}/vessels`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch vessels: ${res.statusText}`);
  const json = await res.json();
  return json.data || [];
}

export async function fetchSources(): Promise<SourceHealth[]> {
  const res = await fetch(`${API_BASE}/sources`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch sources: ${res.statusText}`);
  return res.json();
}

export async function getReplayStatus(): Promise<ReplayStatus> {
  const res = await fetch(`${API_BASE}/replay/status`, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to fetch replay status: ${res.statusText}`);
  return res.json();
}

export async function startReplay(speed = 5.0, scenario?: string): Promise<void> {
  await fetch(`${API_BASE}/replay/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ speed, scenario }),
  });
}

export async function pauseReplay(): Promise<void> {
  await fetch(`${API_BASE}/replay/pause`, { method: "POST" });
}

export async function seekReplay(seconds: number): Promise<void> {
  await fetch(`${API_BASE}/replay/seek`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ seconds }),
  });
}

export async function resetReplay(): Promise<void> {
  await fetch(`${API_BASE}/replay/reset`, { method: "POST" });
}
