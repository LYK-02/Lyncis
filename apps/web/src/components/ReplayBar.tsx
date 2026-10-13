"use client";

import { Play, Pause, RotateCcw, FastForward } from "lucide-react";
import { ReplayStatus } from "@/types/events";

interface ReplayBarProps {
  status: ReplayStatus | null;
  onPlay: (speed?: number) => void;
  onPause: () => void;
  onSeek: (seconds: number) => void;
  onReset: () => void;
  onSetSpeed: (speed: number) => void;
}

export function ReplayBar({
  status,
  onPlay,
  onPause,
  onSeek,
  onReset,
  onSetSpeed,
}: ReplayBarProps) {
  const isPlaying = status?.is_playing ?? false;
  const currentSec = status?.current_time_sec ?? 0;
  const totalSec = status?.total_duration_sec ?? 1800;
  const speed = status?.speed ?? 5.0;

  const formatTime = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = Math.floor(sec % 60);
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const speeds = [1.0, 5.0, 20.0];

  return (
    <div className="h-14 bg-[#0a0a0a]/95 backdrop-blur-md border-t border-white/10 px-4 flex items-center justify-between gap-4 select-none shrink-0 z-30 font-mono text-xs">
      {/* Play/Pause & Reset Controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => (isPlaying ? onPause() : onPlay(speed))}
          className={`flex items-center justify-center w-8 h-8 rounded-full border transition-all cursor-pointer ${
            isPlaying
              ? "bg-[#ffb020]/20 border-[#ffb020] text-[#ffb020] hover:bg-[#ffb020]/30"
              : "bg-[#8cff2e] border-[#8cff2e] text-black hover:bg-[#b6ff6a]"
          }`}
          title={isPlaying ? "Pause Replay" : "Start Replay"}
        >
          {isPlaying ? <Pause className="w-4 h-4 fill-current" /> : <Play className="w-4 h-4 fill-current ml-0.5" />}
        </button>

        <button
          onClick={onReset}
          className="p-1.5 rounded-lg bg-white/5 border border-white/10 text-[#8f8f8f] hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
          title="Reset to 00:00"
        >
          <RotateCcw className="w-3.5 h-3.5" />
        </button>

        {/* Speed Selector */}
        <div className="flex items-center gap-1 bg-black/40 p-1 rounded-md border border-white/5 ml-1">
          {speeds.map((s) => (
            <button
              key={s}
              onClick={() => onSetSpeed(s)}
              className={`px-2 py-0.5 rounded text-[10px] font-bold transition-all cursor-pointer ${
                speed === s
                  ? "bg-[#ffb020]/20 text-[#ffb020] border border-[#ffb020]/40"
                  : "text-[#8f8f8f] hover:text-white"
              }`}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>

      {/* Timeline Scrubber */}
      <div className="flex-1 flex items-center gap-3 max-w-2xl">
        <span className="text-[11px] text-[#d4d4d4] font-bold w-12 text-right">
          {formatTime(currentSec)}
        </span>

        <input
          type="range"
          min="0"
          max={totalSec}
          step="1"
          value={currentSec}
          onChange={(e) => onSeek(parseFloat(e.target.value))}
          className="flex-1 h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer accent-[#ffb020]"
        />

        <span className="text-[11px] text-[#5c5c5c] w-12">
          {formatTime(totalSec)}
        </span>
      </div>

      {/* Replay Scenario Info Tag */}
      <div className="hidden lg:flex items-center gap-2 text-[11px]">
        <span className="px-2 py-0.5 rounded bg-[#ffb020]/10 border border-[#ffb020]/30 text-[#ffb020] font-semibold flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-[#ffb020] animate-pulse" />
          SCENARIO: GOLDEN_REPLAY
        </span>
        <span className="text-[#5c5c5c]">Hormuz / Oman Corridor (14-min Gap Event)</span>
      </div>
    </div>
  );
}
