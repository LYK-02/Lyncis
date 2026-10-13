"use client";

import { useMemo } from "react";
import { VesselTrack, Event } from "@/types/events";
import { Compass, Navigation2 } from "lucide-react";

interface MapConsoleProps {
  vessels: VesselTrack[];
  events: Event[];
  selectedEventId: string | null;
  onSelectVessel: (mmsi: string) => void;
}

export function MapConsole({ vessels, events, selectedEventId, onSelectVessel }: MapConsoleProps) {
  // Map bounds for Hormuz / Gulf of Oman corridor:
  // Lat: 25.0 to 26.0 N (Span 1.0 deg)
  // Lon: 56.5 to 58.0 E (Span 1.5 deg)
  const bounds = {
    minLat: 25.0,
    maxLat: 26.0,
    minLon: 56.5,
    maxLon: 58.0,
  };

  // Convert GPS (lat, lon) to SVG percentages (0 to 100)
  const project = (lat: number, lon: number) => {
    const x = ((lon - bounds.minLon) / (bounds.maxLon - bounds.minLon)) * 100;
    // Invert Y because latitude goes up northward but SVG Y goes down
    const y = (1 - (lat - bounds.minLat) / (bounds.maxLat - bounds.minLat)) * 100;
    return { x: Math.max(2, Math.min(98, x)), y: Math.max(2, Math.min(98, y)) };
  };

  // Identify vessels with active AIS Gaps
  const gapVesselMmsis = useMemo(() => {
    const set = new Set<string>();
    events.forEach((e) => {
      if (e.type === "ais_gap" && e.entity_id) {
        set.add(e.entity_id);
      }
    });
    return set;
  }, [events]);

  return (
    <div className="relative flex-1 h-full bg-[#050505] overflow-hidden select-none">
      {/* Background Water Subtle Bathymetry Gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[#09110d] via-[#050505] to-[#020202]" />

      {/* Grid Overlay */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none stroke-white/5 stroke-[0.5]">
        <defs>
          <pattern id="grid" width="80" height="80" patternUnits="userSpaceOnUse">
            <path d="M 80 0 L 0 0 0 80" fill="none" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>

      {/* Map Content SVG */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
        {/* Navigation Channel Lane (Dashed Lines) */}
        <line x1="5" y1="45" x2="95" y2="70" stroke="#8cff2e" strokeWidth="0.3" strokeDasharray="1.5,1.5" strokeOpacity="0.25" />
        <line x1="5" y1="52" x2="95" y2="77" stroke="#8cff2e" strokeWidth="0.3" strokeDasharray="1.5,1.5" strokeOpacity="0.25" />

        {/* Coastline Aesthetic Contour (Musandam Peninsula hint at top-left) */}
        <path
          d="M 0,0 L 25,0 Q 22,25 15,35 Q 8,42 0,48 Z"
          fill="#111612"
          stroke="rgba(140,255,46,0.15)"
          strokeWidth="0.4"
        />

        {/* Vessel Track Trails */}
        {vessels.map((v) => {
          if (!v.track_points || v.track_points.length < 2) return null;
          const pointsStr = v.track_points
            .map((pt) => {
              const { x, y } = project(pt.lat, pt.lon);
              return `${x},${y}`;
            })
            .join(" ");

          const isTarget = v.mmsi === "572467210" || v.is_sanctioned;
          return (
            <polyline
              key={`trail-${v.mmsi}`}
              points={pointsStr}
              fill="none"
              stroke={isTarget ? "#ff4d4f" : "#8cff2e"}
              strokeWidth={isTarget ? "0.6" : "0.35"}
              strokeOpacity={isTarget ? "0.6" : "0.25"}
              strokeDasharray={isTarget ? "1,1" : "none"}
            />
          );
        })}
      </svg>

      {/* Interactive Vessel Markers (HTML Overlays on top of SVG coordinates) */}
      <div className="absolute inset-0 pointer-events-auto">
        {vessels.map((v) => {
          const { x, y } = project(v.lat, v.lon);
          const isSanctioned = v.is_sanctioned || v.mmsi === "572467210";
          const hasGap = v.has_gap || gapVesselMmsis.has(v.mmsi);
          const rotation = v.heading || v.cog || 0;

          return (
            <div
              key={v.mmsi}
              onClick={() => onSelectVessel(v.mmsi)}
              style={{ left: `${x}%`, top: `${y}%` }}
              className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer group z-10"
            >
              {/* Radar pulse ring if AIS gap detected */}
              {hasGap && (
                <div className="absolute -inset-4 rounded-full border-2 border-[#ffb020] animate-radar pointer-events-none" />
              )}

              {/* Sanctioned Entity Glow Ring */}
              {isSanctioned && (
                <div className="absolute -inset-2 rounded-full border border-red-500/80 animate-ping pointer-events-none opacity-40" />
              )}

              {/* Vessel Marker Chevron */}
              <div
                style={{ transform: `rotate(${rotation}deg)` }}
                className={`relative flex items-center justify-center w-6 h-6 rounded-full transition-transform duration-300 ${
                  isSanctioned
                    ? "bg-red-500/20 text-[#ff4d4f] border border-[#ff4d4f]"
                    : hasGap
                    ? "bg-[#ffb020]/20 text-[#ffb020] border border-[#ffb020]"
                    : "bg-[#8cff2e]/10 text-[#8cff2e] border border-[#8cff2e]/40 hover:bg-[#8cff2e]/20"
                }`}
              >
                <Navigation2 className="w-3.5 h-3.5 fill-current" />
              </div>

              {/* Hover Tooltip Card */}
              <div className="absolute bottom-7 left-1/2 -translate-x-1/2 hidden group-hover:flex flex-col bg-[#0f0f0f]/95 border border-white/15 backdrop-blur-md rounded-md p-2 text-[11px] font-mono shadow-2xl pointer-events-none whitespace-nowrap z-30">
                <div className="flex items-center gap-1.5 font-bold text-white">
                  <span>{v.name || `MMSI ${v.mmsi}`}</span>
                  {isSanctioned && (
                    <span className="text-[9px] px-1 rounded bg-red-500/20 text-red-400 border border-red-500/30">
                      SANCTIONED
                    </span>
                  )}
                  {hasGap && (
                    <span className="text-[9px] px-1 rounded bg-[#ffb020]/20 text-[#ffb020] border border-[#ffb020]/30">
                      AIS GAP
                    </span>
                  )}
                </div>
                <div className="text-[#8f8f8f] text-[10px] flex items-center gap-2 mt-0.5">
                  <span>MMSI: {v.mmsi}</span>
                  {v.imo && <span>IMO: {v.imo}</span>}
                </div>
                <div className="text-[#d4d4d4] text-[10px] flex items-center gap-2 mt-0.5">
                  <span>Speed: {v.sog ?? 0} kn</span>
                  <span>Course: {v.cog ?? 0}°</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Map HUD Legend & Coordinate Indicators */}
      <div className="absolute top-3 left-3 bg-[#0a0a0a]/80 backdrop-blur-md border border-white/10 rounded-lg p-2.5 text-[11px] font-mono text-[#8f8f8f] space-y-1.5 pointer-events-none z-20">
        <div className="flex items-center gap-2 font-bold text-white text-xs">
          <Compass className="w-3.5 h-3.5 text-[#8cff2e]" />
          <span>GULF OF OMAN / HORMUZ CORRIDOR</span>
        </div>
        <div className="flex items-center gap-3 text-[10px]">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-[#8cff2e]" /> Normal Vessel
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-[#ffb020]" /> AIS Gap
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500" /> Sanctioned Entity
          </span>
        </div>
        <div className="text-[9px] text-[#5c5c5c]">
          Bounds: 25.0°N–26.0°N · 56.5°E–58.0°E · Proj: Web Mercator
        </div>
      </div>
    </div>
  );
}
