"use client";

import { Search, Filter, ShieldAlert, Waves, Layers, AlertTriangle } from "lucide-react";

interface FilterRailProps {
  selectedModule: string;
  onSelectModule: (mod: string) => void;
  selectedSeverity: string;
  onSelectSeverity: (sev: string) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  stats: {
    totalEvents: number;
    highSeverity: number;
    activeGaps: number;
    sanctionMatches: number;
  };
}

export function FilterRail({
  selectedModule,
  onSelectModule,
  selectedSeverity,
  onSelectSeverity,
  searchQuery,
  onSearchChange,
  stats,
}: FilterRailProps) {
  const modules = [
    { id: "all", label: "All Signals", icon: Layers },
    { id: "ghostwake", label: "GhostWake (Gaps)", icon: Waves },
    { id: "sanctionweb", label: "SanctionWeb", icon: ShieldAlert },
    { id: "correlation_engine", label: "Correlated (R3)", icon: AlertTriangle },
  ];

  const severities = [
    { id: "all", label: "All Severities" },
    { id: "high", label: "High Severity", color: "text-[#ff4d4f] border-[#ff4d4f]/30" },
    { id: "medium", label: "Medium", color: "text-[#ffb020] border-[#ffb020]/30" },
    { id: "low", label: "Low", color: "text-[#d9e35a] border-[#d9e35a]/30" },
    { id: "info", label: "Info", color: "text-[#6ea8ff] border-[#6ea8ff]/30" },
  ];

  return (
    <aside className="w-64 bg-[#0a0a0a]/75 backdrop-blur-md border-r border-white/10 flex flex-col p-3 gap-4 shrink-0 select-none overflow-y-auto">
      {/* Search Bar */}
      <div className="relative">
        <Search className="absolute left-2.5 top-2.5 w-3.5 h-3.5 text-[#8f8f8f]" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search vessel, MMSI, IMO..."
          className="w-full bg-[#161616] border border-white/10 rounded-lg pl-8 pr-3 py-1.5 text-xs text-[#d4d4d4] placeholder-[#5c5c5c] focus:outline-none focus:border-[#8cff2e]/60 focus:ring-1 focus:ring-[#8cff2e]/40 transition-all font-mono"
        />
      </div>

      {/* Stats Summary Strip */}
      <div className="grid grid-cols-2 gap-2 p-2 rounded-lg bg-black/40 border border-white/5 font-mono text-[11px]">
        <div className="flex flex-col">
          <span className="text-[#8f8f8f]">Signals</span>
          <span className="text-sm font-bold text-white">{stats.totalEvents}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-[#ff4d4f]">High Sev</span>
          <span className="text-sm font-bold text-[#ff4d4f]">{stats.highSeverity}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-[#ffb020]">Active Gaps</span>
          <span className="text-sm font-bold text-[#ffb020]">{stats.activeGaps}</span>
        </div>
        <div className="flex flex-col">
          <span className="text-[#8cff2e]">Sanctioned</span>
          <span className="text-sm font-bold text-[#8cff2e]">{stats.sanctionMatches}</span>
        </div>
      </div>

      {/* Module Filter Group */}
      <div className="flex flex-col gap-1.5">
        <div className="flex items-center gap-1.5 text-[11px] font-semibold text-[#8f8f8f] tracking-wider uppercase">
          <Filter className="w-3 h-3 text-[#8cff2e]" />
          <span>Intelligence Modules</span>
        </div>
        <div className="flex flex-col gap-1">
          {modules.map((m) => {
            const Icon = m.icon;
            const active = selectedModule === m.id;
            return (
              <button
                key={m.id}
                onClick={() => onSelectModule(m.id)}
                className={`flex items-center gap-2 px-2.5 py-1.5 rounded-md text-xs font-medium transition-all text-left ${
                  active
                    ? "bg-[#8cff2e]/15 text-[#8cff2e] border border-[#8cff2e]/40 shadow-[0_0_12px_rgba(140,255,46,0.15)]"
                    : "text-[#8f8f8f] hover:text-[#d4d4d4] hover:bg-white/5"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${active ? "text-[#8cff2e]" : "text-[#5c5c5c]"}`} />
                <span>{m.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Severity Filter Group */}
      <div className="flex flex-col gap-1.5">
        <span className="text-[11px] font-semibold text-[#8f8f8f] tracking-wider uppercase">
          Severity Level
        </span>
        <div className="flex flex-col gap-1">
          {severities.map((s) => {
            const active = selectedSeverity === s.id;
            return (
              <button
                key={s.id}
                onClick={() => onSelectSeverity(s.id)}
                className={`flex items-center justify-between px-2.5 py-1 rounded text-xs transition-all ${
                  active
                    ? "bg-white/10 text-white font-semibold border border-white/20"
                    : "text-[#8f8f8f] hover:text-[#d4d4d4] hover:bg-white/5"
                }`}
              >
                <span className={s.color}>{s.label}</span>
                {active && <span className="w-1.5 h-1.5 rounded-full bg-[#8cff2e]" />}
              </button>
            );
          })}
        </div>
      </div>

      {/* Compliance / Rules Notice */}
      <div className="mt-auto p-2.5 rounded-lg bg-white/5 border border-white/5 text-[10px] text-[#8f8f8f] leading-relaxed">
        <p className="font-semibold text-white/90 mb-0.5">Binding Policy (Rule P1 & P3)</p>
        <p>Lyncis analyzes vessels, infrastructure and events. Observations reflect reported telemetry and do not imply wrongdoing.</p>
      </div>
    </aside>
  );
}
