"use client";

import { useMemo } from "react";
import { VesselTrack, Event } from "@/types/events";
import { Compass, Anchor } from "lucide-react";

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
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-[#0b1510] via-[#050907] to-[#020403]" />

      {/* Grid Overlay */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none stroke-white/5 stroke-[0.5]">
        <defs>
          <pattern id="grid" width="80" height="80" patternUnits="userSpaceOnUse">
            <path d="M 80 0 L 0 0 0 80" fill="none" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>

      {/* Map Content SVG: Coastlines, TSS Lanes, Depth Contours */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
        {/* Depth Contours (Bathymetry lines: 50m, 100m, 200m) */}
        <path d="M 12,0 Q 20,45 18,100" fill="none" stroke="rgba(110,168,255,0.06)" strokeWidth="0.5" strokeDasharray="2,2" />
        <path d="M 22,0 Q 32,50 28,100" fill="none" stroke="rgba(110,168,255,0.08)" strokeWidth="0.5" />
        <path d="M 40,0 Q 52,55 45,100" fill="none" stroke="rgba(110,168,255,0.05)" strokeWidth="0.5" />

        {/* Traffic Separation Scheme (TSS Lanes) */}
        <line x1="5" y1="42" x2="95" y2="68" stroke="#8cff2e" strokeWidth="0.35" strokeDasharray="2,2" strokeOpacity="0.3" />
        <line x1="5" y1="48" x2="95" y2="74" stroke="#ffb020" strokeWidth="0.25" strokeDasharray="1,1" strokeOpacity="0.2" />
        <line x1="5" y1="54" x2="95" y2="80" stroke="#8cff2e" strokeWidth="0.35" strokeDasharray="2,2" strokeOpacity="0.3" />

        {/* Fujairah Offshore Anchorage Polygon */}
        <polygon
          points="2,55 12,50 14,75 2,78"
          fill="rgba(140,255,46,0.03)"
          stroke="#8cff2e"
          strokeWidth="0.3"
          strokeDasharray="1.5,1.5"
          strokeOpacity="0.4"
        />

        {/* West Coastline (UAE / Oman East Coast & Musandam) */}
        <path
          d="M 0,0 L 15,0 C 14,18 10,28 8,42 C 6,55 9,68 7,85 C 5,92 4,96 0,100 Z"
          fill="#0f1511"
          stroke="rgba(140,255,46,0.3)"
          strokeWidth="0.5"
        />

        {/* North/East Coastline (Iran / Jask Approach) */}
        <path
          d="M 68,0 C 72,12 85,18 100,24 L 100,0 Z"
          fill="#121612"
          stroke="rgba(140,255,46,0.2)"
          strokeWidth="0.5"
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
              strokeOpacity={isTarget ? "0.7" : "0.3"}
              strokeDasharray={isTarget ? "1,1" : "none"}
            />
          );
        })}
      </svg>

      {/* Landmarks / Anchorages Labels */}
      <div className="absolute top-[62%] left-[4%] text-[9px] font-mono text-[#8cff2e]/60 pointer-events-none flex items-center gap-1">
        <Anchor className="w-2.5 h-2.5" />
        <span>FUJAIRAH ANCHORAGE (TSS)</span>
      </div>
      <div className="absolute top-[18%] left-[2%] text-[9px] font-mono text-[#8f8f8f]/60 pointer-events-none">
        <span>KHOR FAKKAN</span>
      </div>
      <div className="absolute top-[8%] right-[8%] text-[9px] font-mono text-[#8f8f8f]/60 pointer-events-none">
        <span>JASK APPROACH (IRAN)</span>
      </div>

      {/* Interactive Vessel Markers (Realistic Ship Silhouettes) */}
      <div className="absolute inset-0 pointer-events-auto">
        {vessels.map((v) => {
          const { x, y } = project(v.lat, v.lon);
          const isSanctioned = v.is_sanctioned || v.mmsi === "572467210";
          const hasGap = v.has_gap || gapVesselMmsis.has(v.mmsi);
          const rotation = v.heading || v.cog || 0;
          const sog = v.sog ?? 0;

          // Theme colors based on status
          const hullFill = isSanctioned ? "#3a1012" : hasGap ? "#352409" : "#0d2610";
          const hullStroke = isSanctioned ? "#ff4d4f" : hasGap ? "#ffb020" : "#8cff2e";
          const bridgeFill = isSanctioned ? "#ff4d4f" : hasGap ? "#ffb020" : "#8cff2e";

          return (
            <div
              key={v.mmsi}
              onClick={() => onSelectVessel(v.mmsi)}
              style={{ left: `${x}%`, top: `${y}%` }}
              className="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer group z-10"
            >
              {/* Radar pulse ring if AIS gap detected */}
              {hasGap && (
                <div className="absolute -inset-6 rounded-full border-2 border-[#ffb020] animate-radar pointer-events-none" />
              )}

              {/* Sanctioned Entity Glow Ring */}
              {isSanctioned && (
                <div className="absolute -inset-4 rounded-full border border-red-500 animate-ping pointer-events-none opacity-40" />
              )}

              {/* Realistic Naval Ship Hull SVG */}
              <div
                style={{ transform: `rotate(${rotation}deg)` }}
                className="relative transition-transform duration-300 filter drop-shadow-[0_2px_8px_rgba(0,0,0,0.8)]"
              >
                <svg
                  width="22"
                  height="44"
                  viewBox="-11 -22 22 44"
                  className="overflow-visible"
                >
                  {/* ECDIS Heading Velocity Vector Line (Speed Vector) */}
                  <line
                    x1="0"
                    y1="-16"
                    x2="0"
                    y2={-16 - Math.min(22, Math.max(8, sog * 1.5))}
                    stroke={hullStroke}
                    strokeWidth="1.2"
                    strokeDasharray="2,2"
                    strokeOpacity="0.8"
                  />

                  {/* Stern Wake Bubbles (Visible when vessel is underway) */}
                  {sog > 1 && (
                    <g opacity="0.6">
                      <line x1="-3" y1="14" x2="-6" y2="24" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" strokeDasharray="1.5,1.5" />
                      <line x1="3" y1="14" x2="6" y2="24" stroke="rgba(255,255,255,0.4)" strokeWidth="0.8" strokeDasharray="1.5,1.5" />
                      <line x1="0" y1="14" x2="0" y2="22" stroke="rgba(255,255,255,0.3)" strokeWidth="0.8" />
                    </g>
                  )}

                  {/* Realistic Ship Hull (Pointed Bow, Parallel Sides, Transom Stern) */}
                  <path
                    d="M 0,-16 
                       C 3.5,-12 5.5,-5 5.5,4 
                       L 5,13 
                       L -5,13 
                       L -5.5,4 
                       C -5.5,-5 -3.5,-12 0,-16 Z"
                    fill={hullFill}
                    stroke={hullStroke}
                    strokeWidth="1.2"
                  />

                  {/* Deck Cargo Holds / Tanks Details */}
                  <line x1="-3" y1="-7" x2="3" y2="-7" stroke={hullStroke} strokeWidth="0.8" strokeOpacity="0.6" />
                  <line x1="-3.5" y1="-2" x2="3.5" y2="-2" stroke={hullStroke} strokeWidth="0.8" strokeOpacity="0.6" />

                  {/* Wheelhouse / Bridge Superstructure */}
                  <rect
                    x="-3.5"
                    y="4"
                    width="7"
                    height="5.5"
                    rx="1"
                    fill={bridgeFill}
                    fillOpacity="0.35"
                    stroke={hullStroke}
                    strokeWidth="0.9"
                  />

                  {/* Radar Mast Point */}
                  <circle cx="0" cy="2" r="1" fill={hullStroke} />
                </svg>
              </div>

              {/* Permanent ECDIS Label Tag */}
              <div className="absolute top-1/2 left-4 -translate-y-1/2 ml-1 pointer-events-none hidden md:flex flex-col whitespace-nowrap bg-black/75 backdrop-blur-sm border border-white/10 px-1.5 py-0.5 rounded text-[9px] font-mono shadow-md">
                <span className={`font-bold leading-none ${isSanctioned ? "text-[#ff4d4f]" : hasGap ? "text-[#ffb020]" : "text-white"}`}>
                  {v.name || `MMSI ${v.mmsi}`}
                </span>
                <span className="text-[#8f8f8f] text-[8px] leading-tight mt-0.5">
                  {sog} kn · {Math.round(rotation)}°
                </span>
              </div>

              {/* Detailed Hover Tooltip Card */}
              <div className="absolute bottom-9 left-1/2 -translate-x-1/2 hidden group-hover:flex flex-col bg-[#0f0f0f]/95 border border-white/20 backdrop-blur-md rounded-md p-2.5 text-[11px] font-mono shadow-2xl pointer-events-none whitespace-nowrap z-40">
                <div className="flex items-center gap-1.5 font-bold text-white">
                  <span>{v.name || `MMSI ${v.mmsi}`}</span>
                  {isSanctioned && (
                    <span className="text-[9px] px-1 rounded bg-red-500/20 text-red-400 border border-red-500/40">
                      DESIGNATED ENTITY
                    </span>
                  )}
                  {hasGap && (
                    <span className="text-[9px] px-1 rounded bg-[#ffb020]/20 text-[#ffb020] border border-[#ffb020]/40">
                      AIS GAP DETECTED
                    </span>
                  )}
                </div>
                <div className="text-[#8f8f8f] text-[10px] flex items-center gap-2 mt-1">
                  <span>MMSI: {v.mmsi}</span>
                  {v.imo && <span>IMO: {v.imo}</span>}
                </div>
                <div className="text-[#d4d4d4] text-[10px] flex items-center gap-2 mt-0.5">
                  <span>Speed: {sog} kn</span>
                  <span>Heading: {Math.round(rotation)}°</span>
                </div>
                <div className="text-[9px] text-[#5c5c5c] mt-0.5">
                  Lat: {v.lat.toFixed(4)}° · Lon: {v.lon.toFixed(4)}°
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Map HUD Legend & Coordinate Indicators */}
      <div className="absolute top-3 left-3 bg-[#0a0a0a]/85 backdrop-blur-md border border-white/10 rounded-lg p-2.5 text-[11px] font-mono text-[#8f8f8f] space-y-1.5 pointer-events-none z-20">
        <div className="flex items-center gap-2 font-bold text-white text-xs">
          <Compass className="w-3.5 h-3.5 text-[#8cff2e]" />
          <span>GULF OF OMAN / HORMUZ CORRIDOR</span>
        </div>
        <div className="flex items-center gap-3 text-[10px]">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-[#8cff2e]" /> Active Vessel Hull
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-[#ffb020]" /> AIS Gap Anomaly
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-500" /> Sanctioned Target
          </span>
        </div>
        <div className="text-[9px] text-[#5c5c5c]">
          Real Coordinates · Bounds: 25.0°N–26.0°N · 56.5°E–58.0°E · Proj: Web Mercator
        </div>
      </div>
    </div>
  );
}
