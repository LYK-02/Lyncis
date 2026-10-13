"use client";

import { Event, Severity } from "@/types/events";
import { AlertCircle, AlertTriangle, Info, ShieldAlert, Sparkles } from "lucide-react";

interface EventFeedProps {
  events: Event[];
  selectedEventId: string | null;
  onSelectEvent: (event: Event) => void;
}

export function EventFeed({ events, selectedEventId, onSelectEvent }: EventFeedProps) {
  const getSeverityStyle = (sev: Severity) => {
    switch (sev) {
      case "high":
        return {
          border: "border-l-[#ff4d4f]",
          badge: "bg-red-500/15 text-[#ff4d4f] border-red-500/30",
          icon: AlertCircle,
        };
      case "medium":
        return {
          border: "border-l-[#ffb020]",
          badge: "bg-[#ffb020]/15 text-[#ffb020] border-[#ffb020]/30",
          icon: AlertTriangle,
        };
      case "low":
        return {
          border: "border-l-[#d9e35a]",
          badge: "bg-[#d9e35a]/15 text-[#d9e35a] border-[#d9e35a]/30",
          icon: Info,
        };
      case "info":
      default:
        return {
          border: "border-l-[#6ea8ff]",
          badge: "bg-blue-500/15 text-[#6ea8ff] border-blue-500/30",
          icon: Info,
        };
    }
  };

  return (
    <div className="w-96 bg-[#0b0b0b]/90 backdrop-blur-md border-l border-white/10 flex flex-col h-full select-none shrink-0 z-20">
      {/* Feed Header */}
      <div className="p-3 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-white uppercase tracking-wider font-mono">
            Intelligence Feed
          </span>
          <span className="text-[10px] px-1.5 py-0.2 rounded bg-white/10 text-[#d4d4d4] font-mono">
            {events.length}
          </span>
        </div>
        <span className="text-[10px] text-[#8f8f8f] font-mono">Newest First</span>
      </div>

      {/* Feed List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-2">
        {events.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-48 text-center text-[#8f8f8f] p-4 text-xs font-mono">
            <Info className="w-6 h-6 mb-2 text-[#5c5c5c]" />
            <p>No signal events recorded in current time window.</p>
            <p className="text-[10px] text-[#5c5c5c] mt-1">Start Replay or adjust filters.</p>
          </div>
        ) : (
          events.map((event) => {
            const isSelected = selectedEventId === event.id;
            const style = getSeverityStyle(event.severity);
            const Icon = style.icon;

            return (
              <div
                key={event.id}
                onClick={() => onSelectEvent(event)}
                className={`p-3 rounded-lg border border-white/5 border-l-4 ${style.border} cursor-pointer transition-all ${
                  isSelected
                    ? "bg-white/10 border-white/20 shadow-[0_0_15px_rgba(255,255,255,0.06)]"
                    : "bg-[#141414]/80 hover:bg-[#1a1a1a] hover:border-white/10"
                }`}
              >
                {/* Meta Top Row */}
                <div className="flex items-center justify-between text-[10px] font-mono mb-1.5">
                  <div className="flex items-center gap-1.5">
                    <span className={`flex items-center gap-1 px-1.5 py-0.5 rounded border text-[9px] font-bold uppercase ${style.badge}`}>
                      <Icon className="w-2.5 h-2.5" />
                      {event.severity}
                    </span>
                    <span className="text-[#8f8f8f] uppercase text-[9px]">
                      {event.confidence} CONF
                    </span>
                  </div>
                  <span className="text-[#5c5c5c]">
                    {event.timestamp ? event.timestamp.split("T")[1]?.slice(0, 8) || event.timestamp : "10:15:00"}
                  </span>
                </div>

                {/* Title */}
                <h4 className="text-xs font-semibold text-white leading-snug line-clamp-2">
                  {event.title}
                </h4>

                {/* Summary */}
                <p className="text-[11px] text-[#8f8f8f] line-clamp-2 mt-1 leading-relaxed">
                  {event.summary}
                </p>

                {/* Footer Tags */}
                <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/5 text-[10px] font-mono">
                  <span className="text-[#d4d4d4] font-medium truncate max-w-[150px]">
                    {event.entity_name || `ID: ${event.entity_id}`}
                  </span>
                  <div className="flex items-center gap-1.5">
                    {event.rule_id && (
                      <span className="px-1 rounded bg-white/5 text-[#8cff2e] text-[9px]">
                        [{event.rule_id}]
                      </span>
                    )}
                    <span className="text-[#5c5c5c] lowercase">
                      #{event.source}
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
