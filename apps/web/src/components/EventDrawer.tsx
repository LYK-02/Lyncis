"use client";

import { useState } from "react";
import { Event } from "@/types/events";
import { X, ExternalLink, Copy, Check, Sparkles, AlertTriangle, ShieldCheck, Link2 } from "lucide-react";

interface EventDrawerProps {
  event: Event | null;
  onClose: () => void;
  onSelectParent?: (parentId: string) => void;
}

export function EventDrawer({ event, onClose, onSelectParent }: EventDrawerProps) {
  const [copied, setCopied] = useState(false);

  if (!event) return null;

  const handleCopy = () => {
    const textToCopy = `[LYNCIS EVENT - ${event.id}]\nTitle: ${event.title}\nSeverity: ${event.severity.toUpperCase()} (${event.confidence.toUpperCase()} CONFIDENCE)\nSummary: ${event.summary}\nBrief: ${event.brief || "N/A"}\nReasoning:\n${event.reasoning.map((r) => ` - ${r}`).join("\n")}\nEvidence:\n${event.evidence.map((e) => ` - [${e.source}] ${e.label} (${e.url || "N/A"})`).join("\n")}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="absolute top-0 right-0 w-[420px] h-full bg-[#0d0d0d]/95 backdrop-blur-xl border-l border-white/15 z-40 flex flex-col shadow-2xl animate-in slide-in-from-right duration-200 select-none overflow-hidden">
      {/* Drawer Header */}
      <div className="p-4 border-b border-white/10 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#8cff2e]">
            SIGNAL INSPECTOR
          </span>
          <span className="text-[10px] text-[#8f8f8f] font-mono">[{event.id}]</span>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-md text-[#8f8f8f] hover:text-white hover:bg-white/10 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Drawer Scrollable Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs font-sans">
        {/* Severity & Confidence Banner */}
        <div className="flex items-center justify-between p-2.5 rounded-lg bg-black/40 border border-white/10 font-mono">
          <div className="flex items-center gap-2">
            <span
              className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                event.severity === "high"
                  ? "bg-red-500/20 text-[#ff4d4f] border border-red-500/30"
                  : event.severity === "medium"
                  ? "bg-[#ffb020]/20 text-[#ffb020] border border-[#ffb020]/30"
                  : "bg-[#8cff2e]/20 text-[#8cff2e] border border-[#8cff2e]/30"
              }`}
            >
              {event.severity} SEVERITY
            </span>
            <span className="text-[10px] text-[#8f8f8f] uppercase">
              {event.confidence} CONFIDENCE
            </span>
          </div>
          <span className="text-[10px] text-[#5c5c5c]">
            {event.timestamp ? event.timestamp.split("T")[0] + " " + event.timestamp.split("T")[1]?.slice(0, 8) : ""}
          </span>
        </div>

        {/* Title & Summary */}
        <div className="space-y-1">
          <h3 className="text-sm font-bold text-white leading-snug">
            {event.title}
          </h3>
          <p className="text-xs text-[#d4d4d4] leading-relaxed">
            {event.summary}
          </p>
        </div>

        {/* AI Synthesis Brief (Rule A8: label required) */}
        {event.brief && (
          <div className="p-3 rounded-lg bg-[#8cff2e]/5 border-l-3 border-[#8cff2e] border-white/5 space-y-1.5">
            <div className="flex items-center gap-1.5 text-[10px] font-mono text-[#8cff2e] font-semibold">
              <Sparkles className="w-3 h-3 text-[#8cff2e]" />
              <span>AI-WRITTEN SUMMARY {event.is_fallback && "(DETERMINISTIC TEMPLATE)"}</span>
            </div>
            <p className="text-xs text-[#d4d4d4] leading-relaxed italic">
              &quot;{event.brief}&quot;
            </p>
          </div>
        )}

        {/* Step-by-Step Reasoning (Rule P2) */}
        <div className="space-y-2">
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-[#8f8f8f] uppercase font-semibold">
            <ShieldCheck className="w-3.5 h-3.5 text-[#8cff2e]" />
            <span>Reasoning & Caveats</span>
          </div>
          <ul className="space-y-1.5 text-xs text-[#d4d4d4] bg-white/5 p-3 rounded-lg border border-white/5 list-disc list-inside">
            {event.reasoning.map((r, i) => (
              <li key={i} className="leading-relaxed">
                <span className="text-[#8f8f8f]">{r}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Mandatory Evidence Citations (Rule P2 & A7) */}
        <div className="space-y-2">
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-[#8f8f8f] uppercase font-semibold">
            <ExternalLink className="w-3.5 h-3.5 text-[#8cff2e]" />
            <span>Cited Evidence References</span>
          </div>
          <div className="space-y-1.5 font-mono text-[11px]">
            {event.evidence.map((ev) => (
              <div
                key={ev.id}
                className="p-2.5 rounded bg-black/50 border border-white/10 flex items-start justify-between gap-2"
              >
                <div className="flex flex-col">
                  <span className="text-white font-medium">{ev.label}</span>
                  <span className="text-[10px] text-[#5c5c5c]">Source: {ev.source}</span>
                </div>
                {ev.url ? (
                  <a
                    href={ev.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 px-2 py-1 rounded bg-[#8cff2e]/10 border border-[#8cff2e]/30 text-[#8cff2e] text-[10px] hover:bg-[#8cff2e]/20 transition-all shrink-0"
                  >
                    <span>View Record</span>
                    <ExternalLink className="w-2.5 h-2.5" />
                  </a>
                ) : (
                  <span className="text-[10px] text-[#5c5c5c] shrink-0">In-Stream Record</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Parent Events (for Correlated alerts) */}
        {event.parents && event.parents.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center gap-1.5 text-[11px] font-mono text-[#8f8f8f] uppercase font-semibold">
              <Link2 className="w-3.5 h-3.5 text-[#ffb020]" />
              <span>Correlated Parent Signals ({event.parents.length})</span>
            </div>
            <div className="space-y-1 font-mono text-[11px]">
              {event.parents.map((pId) => (
                <div
                  key={pId}
                  onClick={() => onSelectParent && onSelectParent(pId)}
                  className="p-2 rounded bg-white/5 border border-white/10 text-[#d4d4d4] hover:bg-white/10 hover:border-[#8cff2e]/40 cursor-pointer flex items-center justify-between transition-colors"
                >
                  <span>Event ID: {pId}</span>
                  <span className="text-[9px] text-[#8cff2e]">Inspect &rarr;</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Drawer Action Bar */}
      <div className="p-3 border-t border-white/10 bg-black/60 shrink-0 flex items-center gap-2">
        <button
          onClick={handleCopy}
          className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-white/10 border border-white/15 text-white hover:bg-white/20 transition-all text-xs font-mono font-medium cursor-pointer"
        >
          {copied ? (
            <>
              <Check className="w-3.5 h-3.5 text-[#8cff2e]" />
              <span className="text-[#8cff2e]">Copied Brief!</span>
            </>
          ) : (
            <>
              <Copy className="w-3.5 h-3.5 text-[#8f8f8f]" />
              <span>Copy Cited Brief</span>
            </>
          )}
        </button>
        <button
          onClick={onClose}
          className="px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-[#8f8f8f] hover:text-white hover:bg-white/10 transition-all text-xs font-mono cursor-pointer"
        >
          Close
        </button>
      </div>
    </div>
  );
}
