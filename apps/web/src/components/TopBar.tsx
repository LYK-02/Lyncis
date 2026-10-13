"use client";

import { useState, useEffect } from "react";
import { Radio, Database, ShieldAlert, Activity, WifiOff } from "lucide-react";
import { SourceHealth } from "@/types/events";

interface TopBarProps {
  mode: "live" | "replay" | "offline" | "connecting";
  sources: SourceHealth[];
  onToggleReplay: () => void;
}

export function TopBar({ mode, sources, onToggleReplay }: TopBarProps) {
  const [utcTime, setUtcTime] = useState("");

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setUtcTime(now.toTimeString().split(" ")[0] + " UTC");
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="h-13 bg-[#0a0a0a]/90 backdrop-blur-md border-b border-white/10 px-4 flex items-center justify-between select-none z-30 shrink-0">
      {/* Brand Identity */}
      <div className="flex items-center gap-3">
        <div className="relative flex items-center justify-center w-8 h-8 rounded-lg bg-white/5 border border-white/10">
          {/* Lyncis Radar Eye Mark */}
          <Radio className="w-4.5 h-4.5 text-[#8cff2e]" />
          <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-[#8cff2e] animate-pulse" />
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="text-base font-bold tracking-tight text-white font-mono">LYNCIS</span>
            <span className="text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded bg-white/5 text-[#8cff2e] border border-[#8cff2e]/30 font-medium">
              OSINT v0.1
            </span>
          </div>
          <span className="text-[11px] text-[#8f8f8f] -mt-0.5">Every signal. One story.</span>
        </div>
      </div>

      {/* Center: Mode Badge & Live Status */}
      <div className="flex items-center gap-3">
        {mode === "replay" ? (
          <button
            onClick={onToggleReplay}
            className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#ffb020]/10 border border-[#ffb020]/40 text-[#ffb020] text-xs font-semibold tracking-wider hover:bg-[#ffb020]/20 transition-all cursor-pointer"
          >
            <span className="w-2 h-2 rounded-full bg-[#ffb020] animate-ping" />
            REPLAY MODE (GOLDEN SCENARIO)
          </button>
        ) : mode === "live" ? (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#8cff2e]/10 border border-[#8cff2e]/30 text-[#8cff2e] text-xs font-semibold tracking-wider">
            <span className="w-2 h-2 rounded-full bg-[#8cff2e] animate-live" />
            LIVE MONITORING
          </div>
        ) : mode === "connecting" ? (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[#d4d4d4] text-xs font-semibold tracking-wider">
            <span className="w-2 h-2 rounded-full bg-white/40 animate-pulse" />
            CONNECTING...
          </div>
        ) : (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-semibold tracking-wider">
            <WifiOff className="w-3.5 h-3.5" />
            STREAM OFFLINE
          </div>
        )}

        <div className="hidden md:flex items-center text-xs font-mono text-[#8f8f8f] bg-black/40 px-2.5 py-1 rounded border border-white/5">
          {utcTime || "00:00:00 UTC"}
        </div>
      </div>

      {/* Right: Sources Telemetry */}
      <div className="flex items-center gap-2">
        <span className="text-[11px] text-[#5c5c5c] font-medium mr-1 hidden sm:inline">SOURCES:</span>
        <div className="flex items-center gap-1.5">
          {sources.map((src) => {
            const isOk = src.status === "ok";
            const isDown = src.status === "down";
            return (
              <div
                key={src.source_id}
                title={`${src.name}: ${src.status.toUpperCase()} (${src.message_count} records)`}
                className={`flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-mono border transition-colors ${
                  isOk
                    ? "bg-[#8cff2e]/5 border-[#8cff2e]/20 text-[#d4d4d4]"
                    : isDown
                    ? "bg-red-500/10 border-red-500/30 text-red-300"
                    : "bg-[#ffb020]/5 border-[#ffb020]/20 text-[#8f8f8f]"
                }`}
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full ${
                    isOk ? "bg-[#8cff2e]" : isDown ? "bg-red-500" : "bg-[#ffb020]"
                  }`}
                />
                <span className="truncate max-w-[80px] sm:max-w-none">
                  {src.source_id === "opensanctions" ? "Sanctions" : src.source_id === "aisstream" ? "AISStream" : src.source_id}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </header>
  );
}
